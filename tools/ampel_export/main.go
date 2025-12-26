package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/ossf/gemara/cmd/ampel_export/export"
)

func main() {
	outputDir := flag.String("output", "./ampel-policies", "Output directory for Ampel policy files")
	flag.Parse()
	args := flag.Args()

	if len(args) < 1 {
		fmt.Println("Usage: ampel_export <catalog-path> [flags]")
		fmt.Println("Flags:")
		fmt.Println("  -output <dir>  Output directory for policy files (default: ./ampel-policies)")
		fmt.Println("\nExample:")
		fmt.Println("  ampel_export test-data/good-osps.yml -output ./policies")
		os.Exit(1)
	}

	catalogPath := args[0]

	err := export.CatalogToAmpel(catalogPath, *outputDir)
	if err != nil {
		fmt.Printf("Error converting catalog: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Successfully converted catalog to Ampel policies in %s\n", *outputDir)
}
