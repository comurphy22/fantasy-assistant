package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/ai-atl/nfl-platform/internal/config"
	"github.com/ai-atl/nfl-platform/internal/parquet"
	"github.com/ai-atl/nfl-platform/pkg/mongodb"
	"github.com/joho/godotenv"
	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
)

func main() {
	fmt.Println("=== Game Script Predictor Data Loader ===")
	fmt.Println("Loading games and player stats (2020-2024)...")
	fmt.Println()

	// Load environment
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: .env file not found: %v", err)
	}

	cfg := config.Load()
	ctx := context.Background()

	// Connect to MongoDB
	client, err := mongodb.Connect(ctx, cfg.MongoURI)
	if err != nil {
		log.Fatalf("Failed to connect to MongoDB: %v", err)
	}
	defer client.Disconnect(ctx)

	db := client.Database(cfg.DBName)

	// Create indexes
	fmt.Println("Creating indexes...")
	if err := mongodb.CreateIndexes(ctx, db); err != nil {
		log.Printf("Warning: Failed to create indexes: %v", err)
	}

	// Load games
	fmt.Println("\n📅 Loading games (schedules)...")
	gamesPath := "./nflverse_cache/games.parquet"
	if _, err := os.Stat(gamesPath); os.IsNotExist(err) {
		fmt.Printf("⚠️  Games file not found: %s\n", gamesPath)
	} else {
		data, err := os.ReadFile(gamesPath)
		if err != nil {
			log.Printf("❌ Failed to read games: %v", err)
		} else {
			games, err := parquet.ParseSchedules(data)
			if err != nil {
				log.Printf("❌ Failed to parse games: %v", err)
			} else {
				collection := db.Collection("games")
				inserted := 0
				for _, game := range games {
					filter := bson.M{"game_id": game.GameID}
					update := bson.M{"$set": game}
					opts := options.UpdateOne().SetUpsert(true)

					_, err := collection.UpdateOne(ctx, filter, update, opts)
					if err != nil {
						log.Printf("   ⚠️  Error upserting game %s: %v", game.GameID, err)
						continue
					}
					inserted++
				}
				fmt.Printf("   ✅ Loaded %d games\n", inserted)
			}
		}
	}

	// Load player stats (2020-2024)
	fmt.Println("\n📊 Loading player stats (2020-2024)...")
	years := []int{2020, 2021, 2022, 2023, 2024}
	statsCollection := db.Collection("player_stats")
	totalStats := 0

	for _, year := range years {
		statsPath := fmt.Sprintf("./nflverse_cache/player_stats_regpost_%d.parquet", year)

		if _, err := os.Stat(statsPath); os.IsNotExist(err) {
			fmt.Printf("⚠️  Skipping %d stats (file not found)\n", year)
			continue
		}

		fmt.Printf("📥 Loading player stats from %d...\n", year)

		data, err := os.ReadFile(statsPath)
		if err != nil {
			log.Printf("❌ Failed to read %s: %v", statsPath, err)
			continue
		}

		stats, err := parquet.ParsePlayerStats(data, year, "REGPOST")
		if err != nil {
			log.Printf("❌ Failed to parse stats %d: %v", year, err)
			continue
		}

		if len(stats) == 0 {
			fmt.Printf("⚠️  No stats parsed from %d\n", year)
			continue
		}

		fmt.Printf("   ✓ Parsed %d player stats\n", len(stats))

		// Upsert stats
		inserted := 0
		for _, stat := range stats {
			if stat.NFLID == "" {
				continue
			}

			filter := bson.M{
				"nfl_id":      stat.NFLID,
				"season":      stat.Season,
				"season_type": stat.SeasonType,
			}
			update := bson.M{"$set": stat}
			opts := options.UpdateOne().SetUpsert(true)

			_, err := statsCollection.UpdateOne(ctx, filter, update, opts)
			if err != nil {
				log.Printf("   ⚠️  Error upserting stats: %v", err)
				continue
			}
			inserted++
		}

		totalStats += inserted
		fmt.Printf("   ✅ Inserted/updated %d stats from %d\n", inserted, year)
	}

	// Load weekly stats (for recent performance)
	fmt.Println("\n📈 Loading weekly player stats (2020-2024)...")
	weeklyCollection := db.Collection("player_weekly_stats")
	totalWeekly := 0

	for _, year := range years {
		weeklyPath := fmt.Sprintf("./nflverse_cache/player_stats_weekly_%d.parquet", year)

		if _, err := os.Stat(weeklyPath); os.IsNotExist(err) {
			fmt.Printf("⚠️  Skipping %d weekly stats (file not found)\n", year)
			continue
		}

		fmt.Printf("📥 Loading weekly stats from %d...\n", year)

		data, err := os.ReadFile(weeklyPath)
		if err != nil {
			log.Printf("❌ Failed to read %s: %v", weeklyPath, err)
			continue
		}

		weeklyStats, err := parquet.ParseWeeklyStats(data, year)
		if err != nil {
			log.Printf("❌ Failed to parse weekly stats %d: %v", year, err)
			continue
		}

		if len(weeklyStats) == 0 {
			fmt.Printf("⚠️  No weekly stats parsed from %d\n", year)
			continue
		}

		fmt.Printf("   ✓ Parsed %d weekly stat records\n", len(weeklyStats))

		// Upsert weekly stats
		inserted := 0
		for _, stat := range weeklyStats {
			if stat.NFLID == "" {
				continue
			}

			filter := bson.M{
				"nfl_id": stat.NFLID,
				"season": stat.Season,
				"week":   stat.Week,
			}
			update := bson.M{"$set": stat}
			opts := options.UpdateOne().SetUpsert(true)

			_, err := weeklyCollection.UpdateOne(ctx, filter, update, opts)
			if err != nil {
				log.Printf("   ⚠️  Error upserting weekly stats: %v", err)
				continue
			}
			inserted++
		}

		totalWeekly += inserted
		fmt.Printf("   ✅ Inserted/updated %d weekly stats from %d\n", inserted, year)
	}

	// Summary
	fmt.Printf("\n✅ Data Loading Complete!\n")
	fmt.Printf("📊 Games: %d\n", func() int {
		count, _ := db.Collection("games").CountDocuments(ctx, bson.M{})
		return int(count)
	}())
	fmt.Printf("📊 Player Stats: %d\n", totalStats)
	fmt.Printf("📊 Weekly Stats: %d\n", totalWeekly)
	fmt.Printf("\n🎯 Your Game Script Predictor is now ready!\n")
}
