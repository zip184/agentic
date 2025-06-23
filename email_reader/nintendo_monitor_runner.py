#!/usr/bin/env python3
"""
Nintendo Switch 2 Email Monitor Runner

This script sets up and runs the Nintendo Switch 2 email monitor to watch for 
purchase availability emails from Nintendo.

Usage:
    python nintendo_monitor_runner.py
"""

import asyncio
import time
from services.nintendo_monitor import NintendoSwitch2Monitor, AlertConfig
from services.gmail_service import GmailService
from memory.chroma_memory import ChromaMemoryManager

def setup_monitor():
    """Setup the Nintendo Switch 2 monitor with console and file alerts"""
    
    print("🎮 Setting up Nintendo Switch 2 Email Monitor...")
    
    # Initialize services
    try:
        gmail_service = GmailService()
        print("✅ Gmail service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Gmail service: {e}")
        return None
    
    memory_manager = ChromaMemoryManager()
    monitor = NintendoSwitch2Monitor(gmail_service, memory_manager)
    
    # Configure alerts
    # Console alerts for all notifications
    monitor.add_alert_config(AlertConfig(
        method="console",
        target="",  # Not needed for console
        enabled=True
    ))
    
    # File alerts for logging
    monitor.add_alert_config(AlertConfig(
        method="file",
        target="nintendo_switch2_alerts.log",
        enabled=True
    ))
    
    print("✅ Nintendo Switch 2 monitor configured with:")
    print("   - Console alerts (all notifications)")
    print("   - File logging (nintendo_switch2_alerts.log)")
    print(f"   - Monitoring {len(monitor.nintendo_senders)} Nintendo email domains")
    print(f"   - Watching for {len(monitor.switch2_keywords)} Switch 2 keywords")
    print(f"   - Watching for {len(monitor.purchase_keywords)} purchase keywords")
    
    return monitor

async def run_monitor_continuously(monitor, check_interval_minutes=15):
    """Run the monitor continuously"""
    
    print(f"\n🚀 Starting continuous monitoring (checking every {check_interval_minutes} minutes)")
    print("📧 Will alert when Nintendo emails mention Switch 2 + purchase keywords")
    print("⏱️  Press Ctrl+C to stop monitoring\n")
    
    try:
        await monitor.monitor_emails(check_interval_minutes)
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitor error: {e}")

async def run_single_check(monitor):
    """Run a single check for demonstration"""
    
    print("\n🔍 Running single email check...")
    await monitor._check_for_switch2_emails()
    print("✅ Check completed!")

def main():
    """Main function"""
    
    print("="*60)
    print("🎮 NINTENDO SWITCH 2 EMAIL MONITOR")
    print("="*60)
    print()
    print("This monitor will:")
    print("• Watch for emails from Nintendo domains")
    print("• Look for Switch 2 related keywords")
    print("• Alert when purchase/preorder opportunities are detected")
    print("• Use AI analysis to determine email importance")
    print("• Remember processed emails to avoid duplicate alerts")
    print()
    
    # Setup monitor
    monitor = setup_monitor()
    if not monitor:
        print("❌ Failed to setup monitor. Exiting.")
        return
    
    print("\nChoose monitoring mode:")
    print("1. Run continuous monitoring (recommended)")
    print("2. Run single check (for testing)")
    
    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            # Get check interval
            try:
                interval = input("Check interval in minutes (default: 15): ").strip()
                interval = int(interval) if interval else 15
            except ValueError:
                interval = 15
            
            # Run continuous monitoring
            asyncio.run(run_monitor_continuously(monitor, interval))
            
        elif choice == "2":
            # Run single check
            asyncio.run(run_single_check(monitor))
            
        else:
            print("Invalid choice. Exiting.")
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main() 