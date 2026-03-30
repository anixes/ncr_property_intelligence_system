import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

# Ensure sub-processes can import the package
os.environ["PYTHONPATH"] = (
    str(Path(__file__).parent.absolute())
    if "PATH" not in os.environ
    else str(Path(__file__).parent.absolute()) + os.pathsep + os.environ.get("PYTHONPATH", "")
)


def run_command(command, description):
    print(f"\n[{description}]")
    print(f">> Executing: {command}")
    start_time = time.time()

    result = subprocess.run(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)

    elapsed = time.time() - start_time
    if result.returncode != 0:
        print(f"\n❌ ERROR: Command failed with exit code {result.returncode}")
        print(f">> {command}")
        sys.exit(1)

    print(f"\n✅ SUCCESS: Completed in {elapsed:.1f}s")
    print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="NCR Property Intelligence Unified Pipeline")
    parser.add_argument(
        "--train", action="store_true", help="Run the model training phase (Default)"
    )
    parser.add_argument("--skip-train", action="store_true", help="Skip the model training phase")
    parser.add_argument(
        "--quick-train", action="store_true", help="Run model training with only 1 trial"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🚀 NCR PROPERTY INTELLIGENCE: PURE ML PIPELINE")
    print("=" * 60)

    # Resolve absolute paths for portability
    base_dir = Path(__file__).parent.absolute()

    # Step 1: Preprocessing
    run_command(
        f'"{sys.executable}" "{base_dir / "ncr_property_price_estimation/data/preprocess_buy.py"}"',
        "STEP 1A: Preprocessing Sales Data",
    )
    run_command(
        f'"{sys.executable}" "{base_dir / "ncr_property_price_estimation/data/preprocess_rent.py"}"',
        "STEP 1B: Preprocessing Rental Data",
    )

    # Step 2: Geocoding
    run_command(
        f'"{sys.executable}" "{base_dir / "data/interim/geocoder.py"}"',
        "STEP 2: Geocoding (Sales & Rentals)",
    )

    # Step 3: Geo-Enrichment
    run_command(
        f'"{sys.executable}" "{base_dir / "ncr_property_price_estimation/data/geo_enrichment.py"}" --mode sales',
        "STEP 3A: Geo-Enrichment Sales (H3 Indexing)",
    )
    run_command(
        f'"{sys.executable}" "{base_dir / "ncr_property_price_estimation/data/geo_enrichment.py"}" --mode rentals',
        "STEP 3B: Geo-Enrichment Rentals (H3 Indexing)",
    )

    # Step 4: Model Data Building
    run_command(
        f'"{sys.executable}" "{base_dir / "ncr_property_price_estimation/modeling/data_builder.py"}" --mode sales',
        "STEP 4A: Building Sales Model Dataset",
    )
    run_command(
        f'"{sys.executable}" "{base_dir / "ncr_property_price_estimation/modeling/data_builder.py"}" --mode rentals',
        "STEP 4B: Building Rentals Model Dataset",
    )

    # Step 5: Training
    if not args.skip_train:
        trials_args = "--trials 1" if args.quick_train else "--trials 50"

        run_command(
            f'"{sys.executable}" "{base_dir / "ncr_property_price_estimation/modeling/train.py"}" --mode sales {trials_args}',
            "STEP 5A: Training Sales Model",
        )
        run_command(
            f'"{sys.executable}" "{base_dir / "ncr_property_price_estimation/modeling/train.py"}" --mode rentals {trials_args}',
            "STEP 5B: Training Rentals Model",
        )

    # Step 6: Indexes
    run_command(
        f'"{sys.executable}" "{base_dir / "scripts/build_locality_index.py"}"',
        "STEP 6: Building Locality Index UI Cache",
    )

    print("=" * 60)
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
