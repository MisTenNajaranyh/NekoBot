import shardedBot

if __name__ == "__main__":
    instance = 3
    instances = 4
    shards = 76
    shard_ids = [57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]
    shardedBot.NekoBot(instance=instance, instances=instances, shard_count=shards, shard_ids=shard_ids, max_messages=105).run()
