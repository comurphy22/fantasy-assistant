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
	fmt.Println("=== Loading 2025 Season Data ===")
	fmt.Println("Loading 2025 players for Game Script Predictor...")
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

	// Load 2025 roster
	year := 2025
	cachePath := fmt.Sprintf("./nflverse_cache/roster_%d.parquet", year)

	if _, err := os.Stat(cachePath); os.IsNotExist(err) {
		fmt.Printf("❌ Roster file not found: %s\n", cachePath)
		return
	}

	fmt.Printf("📥 Loading players from %d...\n", year)

	data, err := os.ReadFile(cachePath)
	if err != nil {
		log.Fatalf("❌ Failed to read %s: %v", cachePath, err)
	}

	players, err := parquet.ParseRoster(data, year)
	if err != nil {
		log.Fatalf("❌ Failed to parse roster %d: %v", year, err)
	}

	if len(players) == 0 {
		fmt.Printf("⚠️  No players parsed from %d\n", year)
		return
	}

	fmt.Printf("   ✓ Parsed %d players\n", len(players))

	// Upsert players
	inserted := 0
	for _, player := range players {
		if player.NFLID == "" {
			continue
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

	fmt.Printf("   ✅ Inserted/updated %d players from %d\n", inserted, year)

	// Verify
	count, _ := collection.CountDocuments(ctx, bson.M{"season": 2025})
	fmt.Printf("\n✅ Total 2025 players in database: %d\n", count)

	// Check games
	gamesCount, _ := db.Collection("games").CountDocuments(ctx, bson.M{"season": 2025})
	fmt.Printf("✅ Total 2025 games in database: %d\n", gamesCount)

	fmt.Printf("\n🎯 2025 Game Script Predictor is now ready!\n")
}
