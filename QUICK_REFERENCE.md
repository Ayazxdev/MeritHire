# Quick Reference Guide - Pipeline Management

## ✅ Current Status
- **10/11 services healthy**
- ✅ Passport service: Port 8010 (FIXED)
- ✅ GitHub service: Port 8005 with error handling
- ✅ All pipeline stages operational
- ⚠️ MCP service down (optional, doesn't affect pipeline)

## 🚀 Quick Commands

### Check Service Health
```powershell
# Run from D:\Hiring directory
python verify_pipeline.py
```

### Restart Services
```powershell
# Run from D:\Hiring directory
python agents_services\restart_services.py
```

### Start All Services
```powershell
# Run from D:\Hiring directory
python start_full_system.py
```

## 📍 Important: Always Run from Root Directory

**Correct** ✅:
```powershell
cd D:\Hiring
python verify_pipeline.py
python agents_services\restart_services.py
```

**Wrong** ❌:
```powershell
cd D:\Hiring\backend
python verify_pipeline.py  # This runs the OLD script!
```

## 🔧 What Was Fixed

### 1. Port Configuration
- **Before**: Passport on port 8011, backend expected 8010 → 404 errors
- **After**: Centralized config in `ports_config.py`, passport on 8010 ✅

### 2. Error Handling
- **Before**: GitHub errors crashed pipeline with 500 errors
- **After**: Returns empty data, pipeline continues ✅

### 3. Data Completeness
- **Before**: Missing `anon_id` in passport requests
- **After**: Complete payloads sent ✅

## 🧪 Test the Pipeline

1. **Open frontend**: http://localhost:5173
2. **Submit a test application**
3. **Monitor backend logs** - should see all 10 stages complete:
   ```
   [PIPELINE] Stage 1: ATS ✓
   [PIPELINE] Stage 2: GitHub ✓
   ...
   [PIPELINE] Stage 10: Passport Issuance ✓
   ```

## 🎯 Expected Results

### Before Fixes
```
ERROR: [PIPELINE] PASSPORT failed: Client error '404 Not Found'
ERROR: [PIPELINE] GITHUB failed: Server error '500 Internal Server Error'
ERROR: [PIPELINE] Pipeline failed
```

### After Fixes
```
INFO: [PIPELINE] Stage 10: Passport Issuance
INFO: [PIPELINE] Calling PASSPORT: http://localhost:8010/issue
INFO: [PIPELINE] PASSPORT completed successfully ✓
INFO: [PIPELINE] Pipeline completed for application X
```

## 📁 Key Files

### Configuration
- `agents_services/ports_config.py` - **Single source of truth for ports**
- `backend/app/config.py` - Backend configuration (already correct)

### Services
- `agents_services/passport_service.py` - Port 8010
- `agents_services/github_service.py` - Error handling added
- `backend/app/services/pipeline_orchestrator.py` - Complete payloads

### Tools
- `verify_pipeline.py` - Health check (run from D:\Hiring)
- `agents_services/restart_services.py` - Restart specific services
- `agents_services/service_monitor.py` - Auto-recovery (optional)

## 🐛 Troubleshooting

### Services Won't Start
```powershell
# Check what's running on a port
netstat -ano | findstr ":8010"

# Kill process on port (replace PID)
taskkill /F /PID <PID>

# Restart service
python agents_services\restart_services.py
```

### Pipeline Still Failing
1. Check service health: `python verify_pipeline.py`
2. Look for failed services
3. Check console windows for error messages
4. Restart failed services

### Port Conflicts
1. Edit `agents_services/ports_config.py`
2. Change port number
3. Restart services
4. All references automatically updated

## ✨ What Makes This "Forever"

1. **Centralized Configuration**: Change ports in ONE place
2. **Graceful Degradation**: Services fail safely, pipeline continues
3. **Auto-Recovery**: Optional monitoring can restart failed services
4. **Easy Debugging**: Clear verification and restart tools
5. **Self-Documenting**: Configuration is code, not scattered comments

## 🎓 Best Practices

### When Developing
- Always run commands from `D:\Hiring` root directory
- Use `verify_pipeline.py` to check health before testing
- Use `restart_services.py` after code changes

### When Adding Services
1. Add to `ports_config.py` first
2. Service automatically included in startup
3. No manual port tracking needed

### When Issues Occur
1. Run `verify_pipeline.py` to identify problem
2. Check service console windows
3. Use `restart_services.py` to fix
4. Monitor backend logs

## 📊 Success Metrics

- ✅ No more 404 errors (port mismatch fixed)
- ✅ No more 500 errors (error handling added)
- ✅ Pipeline completes all 10 stages
- ✅ Services can be restarted individually
- ✅ Configuration is centralized
- ✅ System is self-documenting

---

**Remember**: Always run from `D:\Hiring`, not `D:\Hiring\backend`!
