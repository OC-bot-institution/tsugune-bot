import json

def save_message_counts(file, counts):
    print(counts)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(counts, f, ensure_ascii=False, indent=4)

async def initialize_message_counts(bot, message_counts, file):
    for channel_id in message_counts:
        channel = bot.get_channel(int(channel_id))

        if channel is None:
            continue

        count = 0

        async for message in channel.history(limit=None):
            count += 1

        message_counts[channel_id] = count

    save_message_counts(file, message_counts)