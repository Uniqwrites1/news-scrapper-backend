import sqlite3

conn = sqlite3.connect('news_platform.db')
cursor = conn.cursor()

# Check sample articles
cursor.execute('SELECT title, topic, is_priority FROM articles LIMIT 5')
print("Sample articles:")
for row in cursor.fetchall():
    print(f"  {row[0][:50]}... | Topic: {row[1]} | Priority: {row[2]}")

# Check stats
cursor.execute('SELECT COUNT(*) FROM articles')
total = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM articles WHERE topic IS NULL OR topic = ""')
no_topic = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM articles WHERE is_priority = 1')
priority = cursor.fetchone()[0]

print(f"\nTotal articles: {total}")
print(f"Articles with topic: {total - no_topic}")
print(f"Articles without topic: {no_topic}")
print(f"Priority articles: {priority}")

# Check topic distribution
cursor.execute('SELECT topic, COUNT(*) FROM articles GROUP BY topic')
print("\nTopic distribution:")
for topic, count in cursor.fetchall():
    print(f"  {topic}: {count}")

conn.close()
