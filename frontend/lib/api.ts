/**
 * API Client for ExpansionAI Backend
 */

import axios, { AxiosInstance } from 'axios';
import type {
  UniversalSearchResponse,
  DiscoveryResponse,
  SiteAnalysisResponse,
  OutcomeSubmission,
  AccuracyStats,
  Concept,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });
  }

  /**
   * Universal search - detects input type
   */
  async universalSearch(query: string, concept?: Concept): Promise<UniversalSearchResponse> {
    const response = await this.client.post<UniversalSearchResponse>('/api/search', {
      query,
      concept,
    });
    return response.data;
  }

  /**
   * Discovery view - city-wide opportunities
   */
  async discover(city: string, concept: Concept): Promise<DiscoveryResponse> {
    const response = await this.client.post<DiscoveryResponse>('/api/discover', {
      city,
      concept,
    });
    return response.data;
  }

  /**
   * Analyze specific sites
   */
  async analyzeSites(addresses: string[], concept: Concept): Promise<SiteAnalysisResponse> {
    const response = await this.client.post<SiteAnalysisResponse>('/api/analyze', {
      addresses,
      concept,
    });
    return response.data;
  }

  /**
   * Submit outcome after opening
   */
  async submitOutcome(outcome: OutcomeSubmission): Promise<{ status: string; message: string }> {
    const response = await this.client.post('/api/outcomes', outcome);
    return response.data;
  }

  /**
   * Get accuracy statistics
   */
  async getAccuracyStats(): Promise<AccuracyStats> {
    const response = await this.client.get<AccuracyStats>('/api/accuracy');
    return response.data;
  }

  /**
   * Get area detail
   */
  async getAreaDetail(areaId: string, concept: Concept): Promise<any> {
    const response = await this.client.get(`/api/area/${areaId}`, {
      params: { concept }
    });
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  /**
   * NEW: Recommend addresses for concept + city
   */
  async recommend(
    city: string,
    concept: Concept,
    limit: number = 10,
    includeCrime: boolean = false
  ): Promise<{ job_id: string; status: string; stream_url: string }> {
    const response = await this.client.post('/api/recommend', {
      city,
      concept,
      limit,
      include_crime: includeCrime,
    });
    return response.data;
  }

  /**
   * NEW: Get job status (for polling)
   */
  async getJobStatus(jobId: string): Promise<any> {
    const response = await this.client.get(`/api/job/${jobId}`);
    return response.data;
  }

  /**
   * NEW: Get SSE stream URL for job
   */
  getStreamUrl(jobId: string): string {
    return `${API_URL}/api/stream/${jobId}`;
  }

  /**
   * NEW: Generate broker email for an address
   */
  async pursueAddress(
    address: string,
    lat: number,
    lng: number,
    concept: string,
    score: number,
    revenue_min_eur: number,
    revenue_max_eur: number,
    why: string[]
  ): Promise<{ mailto_link: string; gmail_url: string; subject: string; body: string }> {
    const response = await this.client.post('/api/pursue', {
      address,
      lat,
      lng,
      concept,
      score,
      revenue_min_eur,
      revenue_max_eur,
      why,
    });
    return response.data;
  }
}

// Export singleton instance
const api = new APIClient();
export default api;
