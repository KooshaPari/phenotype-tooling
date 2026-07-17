import express from 'express';
import { authenticate } from '../middleware/auth';
import UsageMetricsService from '../services/UsageMetricsService';
import { MetricType, DimensionType } from '../models/UsageMetric';
import logger from '../utils/logger';

const router = express.Router();

// GET /api/metrics/summary - Get usage metrics summary
router.get('/summary', authenticate, async (req, res) => {
  try {
    const startDate = req.query.startDate 
      ? new Date(req.query.startDate as string) 
      : new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // Default to last 30 days
    
    const endDate = req.query.endDate 
      ? new Date(req.query.endDate as string) 
      : new Date();
    
    // Parse dimensions from query params
    const dimensions: Record<string, string> = {};
    
    if (req.query.projectId) dimensions.projectId = req.query.projectId as string;
    if (req.query.agentId) dimensions.agentId = req.query.agentId as string;
    if (req.query.modelId) dimensions.modelId = req.query.modelId as string;
    if (req.query.userId) dimensions.userId = req.query.userId as string;
    if (req.query.organizationId) dimensions.organizationId = req.query.organizationId as string;
    
    const summary = await UsageMetricsService.getUsageSummary({
      startDate,
      endDate,
      dimensions: Object.keys(dimensions).length > 0 ? dimensions : undefined,
    });
    
    res.status(200).json(summary);
  } catch (error) {
    logger.error(`Error getting metrics summary: ${error}`);
    res.status(500).json({ error: 'Failed to retrieve metrics summary' });
  }
});

// GET /api/metrics/timeseries - Get time series data for a specific metric
router.get('/timeseries', authenticate, async (req, res) => {
  try {
    const { metricName, interval } = req.query;
    
    if (!metricName) {
      return res.status(400).json({ error: 'metricName is required' });
    }
    
    const startDate = req.query.startDate 
      ? new Date(req.query.startDate as string) 
      : new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // Default to last 30 days
    
    const endDate = req.query.endDate 
      ? new Date(req.query.endDate as string) 
      : new Date();
    
    // Parse dimensions from query params
    const dimensions: Record<string, string> = {};
    
    if (req.query.projectId) dimensions.projectId = req.query.projectId as string;
    if (req.query.agentId) dimensions.agentId = req.query.agentId as string;
    if (req.query.modelId) dimensions.modelId = req.query.modelId as string;
    if (req.query.userId) dimensions.userId = req.query.userId as string;
    if (req.query.organizationId) dimensions.organizationId = req.query.organizationId as string;
    
    const data = await UsageMetricsService.getTimeSeriesData({
      metricName: metricName as string,
      startDate,
      endDate,
      interval: (interval as 'hour' | 'day' | 'week' | 'month') || 'day',
      dimensions: Object.keys(dimensions).length > 0 ? dimensions : undefined,
    });
    
    res.status(200).json(data);
  } catch (error) {
    logger.error(`Error getting time series data: ${error}`);
    res.status(500).json({ error: 'Failed to retrieve time series data' });
  }
});

// GET /api/metrics/top-consumers - Get top consumers by a specific dimension
router.get('/top-consumers', authenticate, async (req, res) => {
  try {
    const { dimension, metricName, limit } = req.query;
    
    if (!dimension) {
      return res.status(400).json({ error: 'dimension is required' });
    }
    
    // Validate dimension
    if (!Object.values(DimensionType).includes(dimension as DimensionType)) {
      return res.status(400).json({ 
        error: `Invalid dimension. Must be one of: ${Object.values(DimensionType).join(', ')}` 
      });
    }
    
    const startDate = req.query.startDate 
      ? new Date(req.query.startDate as string) 
      : new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // Default to last 30 days
    
    const endDate = req.query.endDate 
      ? new Date(req.query.endDate as string) 
      : new Date();
    
    const data = await UsageMetricsService.getTopConsumers({
      dimension: dimension as DimensionType,
      metricName: metricName as string || 'cost',
      startDate,
      endDate,
      limit: limit ? parseInt(limit as string, 10) : 10,
    });
    
    res.status(200).json(data);
  } catch (error) {
    logger.error(`Error getting top consumers: ${error}`);
    res.status(500).json({ error: 'Failed to retrieve top consumers' });
  }
});

// GET /api/metrics/detailed - Get detailed metrics with filtering and pagination
router.get('/detailed', authenticate, async (req, res) => {
  try {
    const { metricType, groupBy, limit, skip } = req.query;
    
    const startDate = req.query.startDate 
      ? new Date(req.query.startDate as string) 
      : undefined;
    
    const endDate = req.query.endDate 
      ? new Date(req.query.endDate as string) 
      : undefined;
    
    // Parse dimensions from query params
    const dimensions: Record<string, string> = {};
    
    if (req.query.projectId) dimensions.projectId = req.query.projectId as string;
    if (req.query.agentId) dimensions.agentId = req.query.agentId as string;
    if (req.query.modelId) dimensions.modelId = req.query.modelId as string;
    if (req.query.userId) dimensions.userId = req.query.userId as string;
    if (req.query.organizationId) dimensions.organizationId = req.query.organizationId as string;
    if (req.query.workflowId) dimensions.workflowId = req.query.workflowId as string;
    if (req.query.threadId) dimensions.threadId = req.query.threadId as string;
    
    // Parse groupBy fields
    let groupByFields: string[] | undefined;
    
    if (groupBy) {
      groupByFields = (groupBy as string).split(',');
    }
    
    const data = await UsageMetricsService.getMetrics({
      startDate,
      endDate,
      metricType: metricType as MetricType,
      dimensions: Object.keys(dimensions).length > 0 ? dimensions : undefined,
      groupBy: groupByFields,
      limit: limit ? parseInt(limit as string, 10) : 100,
      skip: skip ? parseInt(skip as string, 10) : 0,
    });
    
    res.status(200).json(data);
  } catch (error) {
    logger.error(`Error getting detailed metrics: ${error}`);
    res.status(500).json({ error: 'Failed to retrieve detailed metrics' });
  }
});

// POST /api/metrics/token-usage - Record token usage metrics
router.post('/token-usage', authenticate, async (req, res) => {
  try {
    const {
      tokensIn,
      tokensOut,
      cacheWrites,
      cacheReads,
      contextTokens,
      cost,
      dimensions,
      metadata,
    } = req.body;
    
    if (tokensIn === undefined || tokensOut === undefined || cost === undefined) {
      return res.status(400).json({ 
        error: 'tokensIn, tokensOut, and cost are required fields' 
      });
    }
    
    const metric = await UsageMetricsService.recordTokenUsage({
      tokensIn,
      tokensOut,
      cacheWrites,
      cacheReads,
      contextTokens,
      cost,
      dimensions,
      metadata,
    });
    
    res.status(201).json(metric);
  } catch (error) {
    logger.error(`Error recording token usage: ${error}`);
    res.status(500).json({ error: 'Failed to record token usage' });
  }
});

// POST /api/metrics/api-call - Record API call metrics
router.post('/api-call', authenticate, async (req, res) => {
  try {
    const {
      endpoint,
      statusCode,
      duration,
      errorMessage,
      dimensions,
      metadata,
    } = req.body;
    
    if (!endpoint || duration === undefined) {
      return res.status(400).json({ 
        error: 'endpoint and duration are required fields' 
      });
    }
    
    const metric = await UsageMetricsService.recordApiCall({
      endpoint,
      statusCode,
      duration,
      errorMessage,
      dimensions,
      metadata,
    });
    
    res.status(201).json(metric);
  } catch (error) {
    logger.error(`Error recording API call: ${error}`);
    res.status(500).json({ error: 'Failed to record API call' });
  }
});

// POST /api/metrics/task-execution - Record task execution metrics
router.post('/task-execution', authenticate, async (req, res) => {
  try {
    const {
      startTime,
      endTime,
      duration,
      tokensIn,
      tokensOut,
      cacheWrites,
      cacheReads,
      contextTokens,
      cost,
      dimensions,
      metadata,
    } = req.body;
    
    if (!startTime || !endTime) {
      return res.status(400).json({ 
        error: 'startTime and endTime are required fields' 
      });
    }
    
    const metric = await UsageMetricsService.recordTaskExecution({
      startTime: new Date(startTime),
      endTime: new Date(endTime),
      duration,
      tokensIn,
      tokensOut,
      cacheWrites,
      cacheReads,
      contextTokens,
      cost,
      dimensions,
      metadata,
    });
    
    res.status(201).json(metric);
  } catch (error) {
    logger.error(`Error recording task execution: ${error}`);
    res.status(500).json({ error: 'Failed to record task execution' });
  }
});

// GET /api/metrics/cost-projection - Project cost for a task
router.get('/cost-projection', authenticate, async (req, res) => {
  try {
    const {
      modelId,
      estimatedTokensIn,
      estimatedTokensOut,
      estimatedCacheWrites,
      estimatedCacheReads,
    } = req.query;
    
    if (!modelId || !estimatedTokensIn || !estimatedTokensOut) {
      return res.status(400).json({ 
        error: 'modelId, estimatedTokensIn, and estimatedTokensOut are required fields' 
      });
    }
    
    // In a real implementation, you would fetch the model info from a database or service
    // For now, we'll use a mock model info
    const modelInfo = {
      inputPrice: 3.0, // $3 per million tokens
      outputPrice: 15.0, // $15 per million tokens
      cacheWritesPrice: 3.75, // $3.75 per million tokens
      cacheReadsPrice: 0.3, // $0.30 per million tokens
    };
    
    const projectedCost = UsageMetricsService.projectCost(
      modelInfo as any,
      parseInt(estimatedTokensIn as string, 10),
      parseInt(estimatedTokensOut as string, 10),
      estimatedCacheWrites ? parseInt(estimatedCacheWrites as string, 10) : 0,
      estimatedCacheReads ? parseInt(estimatedCacheReads as string, 10) : 0
    );
    
    res.status(200).json({ projectedCost });
  } catch (error) {
    logger.error(`Error projecting cost: ${error}`);
    res.status(500).json({ error: 'Failed to project cost' });
  }
});

export default router;
