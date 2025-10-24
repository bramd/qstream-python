"""Example usage of the QStream library."""

import asyncio
from qstream import QStreamClient


async def main():
    """Demonstrate QStream library usage."""
    # Connect to device
    async with QStreamClient("192.168.1.165") as client:
        print("=== QStream Device Status ===\n")

        # Get current status
        status = await client.get_status()
        print(f"Current speed: {status.actual_flow}%")
        print(f"Target speed: {status.set_flow}%")
        print(f"Timer active: {status.timer_active}")
        print(f"Schedule enabled: {status.schedule_enabled}")
        print(f"Demand control: {status.demand_control_enabled}")
        print(f"Valve: {'OPEN' if status.valve_open else 'CLOSED'}")

        # Get air quality
        aqi = await client.get_air_quality()
        print(f"\nAir quality index: {aqi}")

        # Get nominal flow rate
        qnom = await client.get_nominal_flow()
        print(f"Nominal flow rate: {qnom}")

        # Get preset levels
        print("\nPreset levels:")
        for i in range(1, 5):
            try:
                level = await client.get_level(i)
                print(f"  Level {i}: {level}%")
                await asyncio.sleep(0.2)  # Small delay between requests
            except Exception as e:
                print(f"  Level {i}: Error - {e}")

        print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
