#!/usr/bin/env python3
"""Test parcel generation with TIF data"""

import sys
from database import SessionLocal
import crud

def test_game_creation():
    """Test creating a game with TIF-based parcels"""
    print("=" * 60)
    print("Testing Parcel Generation with TIF Data")
    print("=" * 60)

    db = SessionLocal()

    zones = ['paris', 'amazon', 'biskra', 'kinshasa']

    for zone_key in zones:
        print(f"\nCreating game for zone: {zone_key}")
        try:
            game = crud.create_game_state(db, zone_key=zone_key)
            parcels = crud.get_parcels(db, game.id)

            print(f"  Game ID: {game.id}")
            print(f"  Parcels created: {len(parcels)}")

            if parcels:
                # Show first 3 parcels
                print(f"  Sample parcels:")
                for i, parcel in enumerate(parcels[:3]):
                    print(f"    {i+1}. Zone: {parcel.zone_id}, Lat: {parcel.lat:.4f}, Lng: {parcel.lng:.4f}, Type: {parcel.parcel_type}, Owned: {parcel.owned}")

        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

    db.close()
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)

if __name__ == "__main__":
    test_game_creation()
