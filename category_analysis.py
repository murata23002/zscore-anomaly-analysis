import argparse
import pandas as pd
import os

def analyze_by_category(input_csv, output_dir, category_column, max_files=None):
    os.makedirs(output_dir, exist_ok=True)

    # Process data in chunks for large datasets
    chunks = pd.read_csv(input_csv, chunksize=100000)
    print(chunks)
    file_count = 0

    results = []

    for chunk in chunks:
        if max_files and file_count >= max_files:
            print("File limit reached. Stopping analysis.")
            break

        # Create a new column combining category and filename
        chunk['combined_filename'] = chunk['category'].astype(str) + "_" + chunk['filename'].astype(str)

        # Classification criteria
        chunk['is_anomalous'] = (chunk['anomaly_distances'] >= 207.19406350700632) | \
                                (chunk['angle_diff'] >= 426.2900228969236)
        chunk['score_category'] = chunk['score'].apply(lambda x: 'High' if x >= 0.5 else 'Low')

        # Create classification labels
        chunk['classification'] = chunk.apply(
            lambda row: f"{'Anomalous Data' if row['is_anomalous'] else 'Normal Data'} + Score {row['score_category']}",
            axis=1
        )

        # Group by combined_filename and classification
        grouped = chunk.groupby(['combined_filename', 'classification']).size().reset_index(name='count')
        results.append(grouped)

        file_count += 1

    # Combine all results
    final_result = pd.concat(results)

    # Pivot table for output (Ensure aggregation uses `sum`)
    pivot_result = final_result.pivot_table(
        index=['combined_filename'],
        columns='classification',
        values='count',
        aggfunc='sum',  # Explicitly use sum
        fill_value=0
    )

    # Save results to CSV
    output_file = os.path.join(output_dir, "category_analysis_results.csv")
    pivot_result.to_csv(output_file)
    print(f"Analysis completed. Results saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True, help="Input CSV file path")
    parser.add_argument("--output_dir", required=True, help="Output directory for results")
    parser.add_argument("--category_column", required=True, help="Category column to group data")
    parser.add_argument("--max_files", type=int, default=2000, help="Maximum number of chunks to process")

    args = parser.parse_args()

    print(f"Starting category-based analysis for {args.category_column}...")
    analyze_by_category(args.input_csv, args.output_dir, args.category_column, args.max_files)
    print("Category-based analysis completed.")
