import UsageMetric, { IUsageMetric, MetricType, DimensionType } from '../models/UsageMetric';
import logger from '../utils/logger';
import { ModelInfo } from '../shared/api';

/**
 * Service for recording and retrieving usage metrics
 */
class UsageMetricsService {
  /**
   * Record token usage metrics
   */
  async recordTokenUsage({
    tokensIn,
    tokensOut,
    cacheWrites,
    cacheReads,
    contextTokens,
    cost,
    dimensions,
    metadata,
  }: {
    tokensIn: number;
    tokensOut: number;
    cacheWrites?: number;
    cacheReads?: number;
    contextTokens?: number;
    cost: number;
    dimensions: {
      projectId?: string;
      sessionId?: string;
      agentId?: string;
      modelId?: string;
      modelName?: string;
      roleId?: string;
      userId?: string;
      organizationId?: string;
      workflowId?: string;
      threadId?: string;
    };
    metadata?: Record<string, any>;
  }): Promise<IUsageMetric> {
    try {
      const metric = new UsageMetric({
        timestamp: new Date(),
        metricType: MetricType.TOKEN_USAGE,
        tokensIn,
        tokensOut,
        cacheWrites,
        cacheReads,
        contextTokens,
        cost,
        dimensions,
        metadata,
      });

      await metric.save();
      return metric;
    } catch (error) {
      logger.error(`Error recording token usage: ${error}`);
      throw error;
    }
  }

  /**
   * Record API call metrics
   */
  async recordApiCall({
    endpoint,
    statusCode,
    duration,
    errorMessage,
    dimensions,
    metadata,
  }: {
    endpoint: string;
    statusCode?: number;
    duration: number;
    errorMessage?: string;
    dimensions: {
      projectId?: string;
      sessionId?: string;
      agentId?: string;
      modelId?: string;
      modelName?: string;
      roleId?: string;
      userId?: string;
      organizationId?: string;
      workflowId?: string;
      threadId?: string;
    };
    metadata?: Record<string, any>;
  }): Promise<IUsageMetric> {
    try {
      const metric = new UsageMetric({
        timestamp: new Date(),
        metricType: MetricType.API_CALL,
        endpoint,
        statusCode,
        duration,
        errorMessage,
        dimensions,
        metadata,
      });

      await metric.save();
      return metric;
    } catch (error) {
      logger.error(`Error recording API call: ${error}`);
      throw error;
    }
  }

  /**
   * Record task execution metrics
   */
  async recordTaskExecution({
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
  }: {
    startTime: Date;
    endTime: Date;
    duration?: number;
    tokensIn?: number;
    tokensOut?: number;
    cacheWrites?: number;
    cacheReads?: number;
    contextTokens?: number;
    cost?: number;
    dimensions: {
      projectId?: string;
      sessionId?: string;
      agentId?: string;
      modelId?: string;
      modelName?: string;
      roleId?: string;
      userId?: string;
      organizationId?: string;
      workflowId?: string;
      threadId?: string;
    };
    metadata?: Record<string, any>;
  }): Promise<IUsageMetric> {
    try {
      // Calculate duration if not provided
      const calculatedDuration = duration || (endTime.getTime() - startTime.getTime());
      
      const metric = new UsageMetric({
        timestamp: endTime,
        metricType: MetricType.TASK_EXECUTION,
        startTime,
        endTime,
        duration: calculatedDuration,
        tokensIn,
        tokensOut,
        cacheWrites,
        cacheReads,
        contextTokens,
        cost,
        dimensions,
        metadata,
      });

      await metric.save();
      return metric;
    } catch (error) {
      logger.error(`Error recording task execution: ${error}`);
      throw error;
    }
  }

  /**
   * Calculate estimated cost based on model info and token counts
   */
  calculateCost(
    modelInfo: ModelInfo,
    tokensIn: number,
    tokensOut: number,
    cacheWrites: number = 0,
    cacheReads: number = 0
  ): number {
    const inputCost = ((modelInfo.inputPrice || 0) / 1_000_000) * tokensIn;
    const outputCost = ((modelInfo.outputPrice || 0) / 1_000_000) * tokensOut;
    const cacheWritesCost = ((modelInfo.cacheWritesPrice || 0) / 1_000_000) * cacheWrites;
    const cacheReadsCost = ((modelInfo.cacheReadsPrice || 0) / 1_000_000) * cacheReads;
    
    return inputCost + outputCost + cacheWritesCost + cacheReadsCost;
  }

  /**
   * Project cost for a given task based on model and estimated tokens
   */
  projectCost(
    modelInfo: ModelInfo,
    estimatedTokensIn: number,
    estimatedTokensOut: number,
    estimatedCacheWrites: number = 0,
    estimatedCacheReads: number = 0
  ): number {
    return this.calculateCost(
      modelInfo,
      estimatedTokensIn,
      estimatedTokensOut,
      estimatedCacheWrites,
      estimatedCacheReads
    );
  }

  /**
   * Get usage metrics with filtering and aggregation
   */
  async getMetrics({
    startDate,
    endDate,
    metricType,
    dimensions,
    groupBy,
    limit = 100,
    skip = 0,
  }: {
    startDate?: Date;
    endDate?: Date;
    metricType?: MetricType;
    dimensions?: Record<string, string>;
    groupBy?: string[];
    limit?: number;
    skip?: number;
  }): Promise<any> {
    try {
      // Build query
      const query: any = {};
      
      if (startDate || endDate) {
        query.timestamp = {};
        if (startDate) query.timestamp.$gte = startDate;
        if (endDate) query.timestamp.$lte = endDate;
      }
      
      if (metricType) {
        query.metricType = metricType;
      }
      
      // Add dimension filters
      if (dimensions) {
        for (const [key, value] of Object.entries(dimensions)) {
          query[`dimensions.${key}`] = value;
        }
      }
      
      // If groupBy is provided, use aggregation
      if (groupBy && groupBy.length > 0) {
        const groupByFields: Record<string, any> = {};
        
        // Add groupBy fields to the group stage
        for (const field of groupBy) {
          if (field.startsWith('dimensions.')) {
            groupByFields[field.replace('dimensions.', '')] = `$${field}`;
          } else {
            groupByFields[field] = `$${field}`;
          }
        }
        
        // Add time period if needed
        if (groupBy.includes('day')) {
          groupByFields.day = { $dayOfMonth: '$timestamp' };
          groupByFields.month = { $month: '$timestamp' };
          groupByFields.year = { $year: '$timestamp' };
        } else if (groupBy.includes('month')) {
          groupByFields.month = { $month: '$timestamp' };
          groupByFields.year = { $year: '$timestamp' };
        } else if (groupBy.includes('hour')) {
          groupByFields.hour = { $hour: '$timestamp' };
          groupByFields.day = { $dayOfMonth: '$timestamp' };
          groupByFields.month = { $month: '$timestamp' };
          groupByFields.year = { $year: '$timestamp' };
        }
        
        // Build aggregation pipeline
        const pipeline = [
          { $match: query },
          {
            $group: {
              _id: groupByFields,
              count: { $sum: 1 },
              totalTokensIn: { $sum: '$tokensIn' },
              totalTokensOut: { $sum: '$tokensOut' },
              totalCacheWrites: { $sum: '$cacheWrites' },
              totalCacheReads: { $sum: '$cacheReads' },
              totalContextTokens: { $sum: '$contextTokens' },
              totalCost: { $sum: '$cost' },
              avgDuration: { $avg: '$duration' },
              minDuration: { $min: '$duration' },
              maxDuration: { $max: '$duration' },
              firstTimestamp: { $min: '$timestamp' },
              lastTimestamp: { $max: '$timestamp' },
            }
          },
          { $sort: { lastTimestamp: -1 } },
          { $skip: skip },
          { $limit: limit }
        ];
        
        return await UsageMetric.aggregate(pipeline);
      } else {
        // Simple find query with pagination
        return await UsageMetric.find(query)
          .sort({ timestamp: -1 })
          .skip(skip)
          .limit(limit);
      }
    } catch (error) {
      logger.error(`Error retrieving metrics: ${error}`);
      throw error;
    }
  }

  /**
   * Get usage summary for a specific time period
   */
  async getUsageSummary({
    startDate,
    endDate,
    dimensions,
  }: {
    startDate: Date;
    endDate: Date;
    dimensions?: Record<string, string>;
  }): Promise<any> {
    try {
      const query: any = {
        timestamp: {
          $gte: startDate,
          $lte: endDate,
        },
      };
      
      // Add dimension filters
      if (dimensions) {
        for (const [key, value] of Object.entries(dimensions)) {
          query[`dimensions.${key}`] = value;
        }
      }
      
      const pipeline = [
        { $match: query },
        {
          $group: {
            _id: null,
            totalTokensIn: { $sum: '$tokensIn' },
            totalTokensOut: { $sum: '$tokensOut' },
            totalCacheWrites: { $sum: '$cacheWrites' },
            totalCacheReads: { $sum: '$cacheReads' },
            totalContextTokens: { $sum: '$contextTokens' },
            totalCost: { $sum: '$cost' },
            totalApiCalls: {
              $sum: {
                $cond: [{ $eq: ['$metricType', MetricType.API_CALL] }, 1, 0]
              }
            },
            totalTasks: {
              $sum: {
                $cond: [{ $eq: ['$metricType', MetricType.TASK_EXECUTION] }, 1, 0]
              }
            },
            avgTaskDuration: {
              $avg: {
                $cond: [
                  { $eq: ['$metricType', MetricType.TASK_EXECUTION] },
                  '$duration',
                  null
                ]
              }
            },
            uniqueAgents: { $addToSet: '$dimensions.agentId' },
            uniqueModels: { $addToSet: '$dimensions.modelId' },
            uniqueProjects: { $addToSet: '$dimensions.projectId' },
          }
        },
        {
          $project: {
            _id: 0,
            totalTokensIn: 1,
            totalTokensOut: 1,
            totalCacheWrites: 1,
            totalCacheReads: 1,
            totalContextTokens: 1,
            totalCost: 1,
            totalApiCalls: 1,
            totalTasks: 1,
            avgTaskDuration: 1,
            uniqueAgentCount: { $size: '$uniqueAgents' },
            uniqueModelCount: { $size: '$uniqueModels' },
            uniqueProjectCount: { $size: '$uniqueProjects' },
          }
        }
      ];
      
      const results = await UsageMetric.aggregate(pipeline);
      return results[0] || {
        totalTokensIn: 0,
        totalTokensOut: 0,
        totalCacheWrites: 0,
        totalCacheReads: 0,
        totalContextTokens: 0,
        totalCost: 0,
        totalApiCalls: 0,
        totalTasks: 0,
        avgTaskDuration: 0,
        uniqueAgentCount: 0,
        uniqueModelCount: 0,
        uniqueProjectCount: 0,
      };
    } catch (error) {
      logger.error(`Error retrieving usage summary: ${error}`);
      throw error;
    }
  }

  /**
   * Get time series data for a specific metric
   */
  async getTimeSeriesData({
    metricName,
    startDate,
    endDate,
    interval = 'day',
    dimensions,
  }: {
    metricName: string;
    startDate: Date;
    endDate: Date;
    interval?: 'hour' | 'day' | 'week' | 'month';
    dimensions?: Record<string, string>;
  }): Promise<any[]> {
    try {
      const query: any = {
        timestamp: {
          $gte: startDate,
          $lte: endDate,
        },
      };
      
      // Add dimension filters
      if (dimensions) {
        for (const [key, value] of Object.entries(dimensions)) {
          query[`dimensions.${key}`] = value;
        }
      }
      
      // Define date grouping based on interval
      let dateGroup: any = {};
      
      switch (interval) {
        case 'hour':
          dateGroup = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
            day: { $dayOfMonth: '$timestamp' },
            hour: { $hour: '$timestamp' },
          };
          break;
        case 'day':
          dateGroup = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
            day: { $dayOfMonth: '$timestamp' },
          };
          break;
        case 'week':
          dateGroup = {
            year: { $year: '$timestamp' },
            week: { $week: '$timestamp' },
          };
          break;
        case 'month':
          dateGroup = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
          };
          break;
      }
      
      // Define metric aggregation
      let metricAggregation: any = {};
      
      switch (metricName) {
        case 'tokensIn':
        case 'tokensOut':
        case 'cacheWrites':
        case 'cacheReads':
        case 'contextTokens':
        case 'cost':
          metricAggregation = { $sum: `$${metricName}` };
          break;
        case 'duration':
          metricAggregation = { $avg: '$duration' };
          break;
        case 'apiCalls':
          metricAggregation = {
            $sum: {
              $cond: [{ $eq: ['$metricType', MetricType.API_CALL] }, 1, 0]
            }
          };
          break;
        case 'tasks':
          metricAggregation = {
            $sum: {
              $cond: [{ $eq: ['$metricType', MetricType.TASK_EXECUTION] }, 1, 0]
            }
          };
          break;
        default:
          metricAggregation = { $sum: 1 }; // Default to count
      }
      
      const pipeline = [
        { $match: query },
        {
          $group: {
            _id: dateGroup,
            value: metricAggregation,
            timestamp: { $min: '$timestamp' },
          }
        },
        { $sort: { timestamp: 1 } },
        {
          $project: {
            _id: 0,
            timestamp: 1,
            value: 1,
          }
        }
      ];
      
      return await UsageMetric.aggregate(pipeline);
    } catch (error) {
      logger.error(`Error retrieving time series data: ${error}`);
      throw error;
    }
  }

  /**
   * Get top consumers by a specific dimension
   */
  async getTopConsumers({
    dimension,
    metricName = 'cost',
    startDate,
    endDate,
    limit = 10,
  }: {
    dimension: DimensionType;
    metricName?: string;
    startDate: Date;
    endDate: Date;
    limit?: number;
  }): Promise<any[]> {
    try {
      const query: any = {
        timestamp: {
          $gte: startDate,
          $lte: endDate,
        },
      };
      
      // Ensure the dimension exists
      query[`dimensions.${dimension}Id`] = { $exists: true };
      
      // Define metric aggregation
      let metricAggregation: any = {};
      
      switch (metricName) {
        case 'tokensIn':
        case 'tokensOut':
        case 'cacheWrites':
        case 'cacheReads':
        case 'contextTokens':
        case 'cost':
          metricAggregation = { $sum: `$${metricName}` };
          break;
        case 'duration':
          metricAggregation = { $avg: '$duration' };
          break;
        case 'apiCalls':
          metricAggregation = {
            $sum: {
              $cond: [{ $eq: ['$metricType', MetricType.API_CALL] }, 1, 0]
            }
          };
          break;
        case 'tasks':
          metricAggregation = {
            $sum: {
              $cond: [{ $eq: ['$metricType', MetricType.TASK_EXECUTION] }, 1, 0]
            }
          };
          break;
        default:
          metricAggregation = { $sum: 1 }; // Default to count
      }
      
      const pipeline = [
        { $match: query },
        {
          $group: {
            _id: `$dimensions.${dimension}Id`,
            name: { $first: `$dimensions.${dimension}Name` },
            value: metricAggregation,
            count: { $sum: 1 },
          }
        },
        { $sort: { value: -1 } },
        { $limit: limit },
        {
          $project: {
            _id: 0,
            id: '$_id',
            name: 1,
            value: 1,
            count: 1,
          }
        }
      ];
      
      return await UsageMetric.aggregate(pipeline);
    } catch (error) {
      logger.error(`Error retrieving top consumers: ${error}`);
      throw error;
    }
  }
}

export default new UsageMetricsService();
