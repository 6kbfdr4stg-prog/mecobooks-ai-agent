from server import sync_reports_to_db

if __name__ == "__main__":
    print("🔄 Forcing report sync...")
    sync_reports_to_db()
    print("✅ Sync complete!")
