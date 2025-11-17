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
	fmt.Println("=== Quick Player Loader (2020-2024) ===")
	fmt.Println("Loading players from cached roster files...")
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

	collection := db.Collection("players")
	totalInserted := 0

	// Load roster files from cache (2020-2024)
	years := []int{2020, 2021, 2022, 2023, 2024}

	for _, year := range years {
		cachePath := fmt.Sprintf("./nflverse_cache/roster_%d.parquet", year)

		if _, err := os.Stat(cachePath); os.IsNotExist(err) {
			fmt.Printf("⚠️  Skipping %d (file not found: %s)\n", year, cachePath)
			continue
		}

		fmt.Printf("📥 Loading players from %d...\n", year)

		data, err := os.ReadFile(cachePath)
		if err != nil {
			log.Printf("❌ Failed to read %s: %v", cachePath, err)
			continue
		}

		players, err := parquet.ParseRoster(data, year)
		if err != nil {
			log.Printf("❌ Failed to parse roster %d: %v", year, err)
			continue
		}

		if len(players) == 0 {
			fmt.Printf("⚠️  No players parsed from %d\n", year)
			continue
		}

		fmt.Printf("   ✓ Parsed %d players\n", len(players))

		// Upsert players
		inserted := 0
		for _, player := range players {
			if player.NFLID == "" {
				continue // Skip players without NFL ID
			}

			filter := bson.M{
				"nfl_id": player.NFLID,
				"season": player.Season,
			}
			update := bson.M{"$set": player}
			opts := options.UpdateOne().SetUpsert(true)

			_, err := collection.UpdateOne(ctx, filter, update, opts)
			if err != nil {
				log.Printf("   ⚠️  Error upserting player %s: %v", player.Name, err)
				continue
			}
			inserted++
		}

		totalInserted += inserted
		fmt.Printf("   ✅ Inserted/updated %d players from %d\n", inserted, year)
	}

	fmt.Printf("\n✅ Total: %d players loaded!\n", totalInserted)
	
	// Verify
	count, _ := collection.CountDocuments(ctx, bson.M{})
	fmt.Printf("📊 Total players in database: %d\n", count)
}

