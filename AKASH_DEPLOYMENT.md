# Akash Network Deployment Guide

## Quick Deploy

### 1. Prerequisites
- Akash CLI installed (`akash`)
- Akash wallet with AKT tokens
- Keplr wallet or CLI wallet configured

### 2. Environment Setup

Edit `akash-deploy.yaml` and fill in your API keys:
```yaml
- DISCORD_TOKEN=your_discord_bot_token
- OPENROUTER_API_KEY=your_openrouter_key  
- OPENAI_API_KEY=your_openai_key
- PINECONE_API_KEY=your_pinecone_key
```

### 3. Deploy to Akash

```bash
# Create deployment
akash tx deployment create akash-deploy.yaml --from wallet --chain-id akashnet-2

# Get deployment ID
akash query deployment list --owner [your-address]

# Check bids
akash query market bid list --owner [your-address] --dseq [deployment-seq]

# Accept bid
akash tx market lease create --dseq [deployment-seq] --provider [provider-address] --from wallet

# Send manifest
akash provider send-manifest akash-deploy.yaml --dseq [deployment-seq] --provider [provider-address] --from wallet

# Check logs
akash provider lease-logs --dseq [deployment-seq] --provider [provider-address] --from wallet
```

## Configuration Details

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Discord bot token | `MTIz...abc` |
| `OPENROUTER_API_KEY` | OpenRouter API key | `sk-or-v1-...` |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | `sk-...` |
| `PINECONE_API_KEY` | Pinecone vector DB key | `abc123...` |

### Optional Performance Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `YOLO_MODE` | `false` | Enable unlimited transcript processing |
| `RAG_CHUNK_SIZE` | `1500` | Characters per chunk for embeddings |
| `RAG_CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `MAX_TOKENS` | `4096` | Max tokens for AI responses |
| `TEMPERATURE` | `0.7` | AI creativity (0-1) |
| `QUERY_TOP_K` | `5` | Number of search results |
| `SIMILARITY_THRESHOLD` | `0.3` | Min similarity for results |

### Resource Requirements

**Minimum (in SDL):**
- CPU: 0.5 units
- Memory: 512Mi
- Storage: 1Gi

**Recommended (default):**
- CPU: 1.0 units  
- Memory: 1Gi
- Storage: 2Gi

**High Performance:**
- CPU: 2.0 units
- Memory: 2Gi
- Storage: 4Gi

## Cost Estimation

With default settings:
- **CPU**: 1.0 units × 100 uakt = 100 uakt/block
- **Memory**: 1Gi × 100 uakt = 100 uakt/block
- **Storage**: 2Gi × 100 uakt = 200 uakt/block
- **Total**: ~400 uakt/block

Monthly cost: ~10-15 AKT (depending on AKT price)

## Monitoring

### Check Health
```bash
akash provider lease-status --dseq [deployment-seq] --provider [provider-address]
```

### View Logs
```bash
# Stream logs
akash provider lease-logs --dseq [deployment-seq] --provider [provider-address] --follow

# Last 100 lines
akash provider lease-logs --dseq [deployment-seq] --provider [provider-address] --tail 100
```

### Update Deployment

To update with new environment variables or image:

1. Close current deployment:
```bash
akash tx deployment close --dseq [deployment-seq] --from wallet
```

2. Edit `akash-deploy.yaml` with changes

3. Create new deployment (repeat deploy steps)

## Troubleshooting

### Bot Not Connecting
- Verify `DISCORD_TOKEN` is correct
- Check logs for connection errors
- Ensure bot has proper Discord permissions

### High Memory Usage
- Reduce `RAG_CHUNK_SIZE` to 1000
- Set `YOLO_MODE=false`
- Lower `CONVERSATION_HISTORY_LIMIT`

### API Rate Limits
- Switch to different OpenRouter model
- Implement caching (future feature)
- Reduce `QUERY_TOP_K`

## Provider Selection

Recommended providers for Discord bots:
- Praetor (reliable uptime)
- Overclock Labs (official)
- Europlots (EU region)

Check provider uptime at: https://akashlytics.com/providers

## Security Notes

1. **Never commit SDL with real API keys**
2. Use environment variable substitution in production
3. Consider using Akash secrets (when available)
4. Rotate API keys regularly
5. Monitor usage for unusual activity

## Support

- **Akash Discord**: https://discord.gg/akash
- **Bot Issues**: https://github.com/arealicehole/miyu-data/issues
- **Akash Docs**: https://docs.akash.network