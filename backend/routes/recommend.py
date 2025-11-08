"""
Recommend Routes - Address-first recommendation flow

NEW: This is the primary user flow
POST /api/recommend - Start recommendation job
GET /api/stream/{job_id} - SSE stream for job progress
GET /api/job/{job_id} - Poll job status
"""

import asyncio
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from datetime import datetime

from models.schemas import (
    RecommendRequest,
    RecommendResponse,
    RecommendedAddress,
    WeightsInfo,
    JobStatusResponse,
    PursueRequest,
    PursueResponse
)
from services.job_manager import job_manager, StageStatus
from services.address_generator import AddressGenerator
from services.statfin import StatFinService
from services.population_grid import PopulationGridService
from services.digitransit import DigitransitService

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
statfin_service = StatFinService()
pop_grid_service = PopulationGridService()
digitransit_service = DigitransitService()

address_generator = AddressGenerator(
    statfin_service=statfin_service,
    population_grid_service=pop_grid_service,
    digitransit_service=digitransit_service
)

# Store background task references to prevent garbage collection
background_tasks = set()


@router.post("/api/recommend")
async def recommend_addresses(
    request: RecommendRequest
):
    """
    Start address recommendation job

    Returns job_id immediately and processes in background
    Client should connect to /api/stream/{job_id} for progress updates
    """
    print(f"\n{'='*60}")
    print(f"🎯 NEW RECOMMENDATION REQUEST")
    print(f"   City: {request.city}")
    print(f"   Concept: {request.concept}")
    print(f"   Limit: {request.limit}")
    print(f"   Include Crime: {request.include_crime}")
    print(f"{'='*60}\n")
    
    # Create job
    job_id = job_manager.create_job(
        city=request.city,
        concept=request.concept,
        limit=request.limit,
        include_crime=request.include_crime
    )
    
    print(f"✅ Created job: {job_id}")
    print(f"📤 Creating asyncio task with ensure_future()")

    # Use asyncio.ensure_future to start task immediately
    asyncio.ensure_future(
        run_recommendation_job(
            job_id=job_id,
            city=request.city,
            concept=request.concept,
            limit=request.limit,
            include_crime=request.include_crime
        )
    )
    
    print(f"✅ Task created and scheduled")

    return {
        "job_id": job_id,
        "status": "processing",
        "stream_url": f"/api/stream/{job_id}"
    }


@router.get("/api/stream/{job_id}")
async def stream_job_progress(job_id: str):
    """
    SSE stream for job progress

    Events sent:
    - stage updates (GEO, DEMO, COMP, TRANSIT, TRAFFIC, RENTS, REVENUE)
    - completion with full result
    - error if job fails
    """
    print(f"\n📡 SSE CONNECTION OPENED")
    print(f"   Job ID: {job_id}")
    print(f"   Streaming events...\n")
    
    job = job_manager.get_job(job_id)
    if not job:
        print(f"❌ Job {job_id} not found!")
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    async def event_generator():
        """Generate SSE events"""
        event_count = 0
        async for event in job_manager.stream_job_events(job_id):
            event_count += 1
            # Format as SSE
            event_type = event.get('stage', 'message')
            data = json.dumps(event)
            
            # Log each event sent
            print(f"   📤 Event #{event_count}: {event_type} - {event.get('status', 'N/A')}")
            
            yield f"event: {event_type}\ndata: {data}\n\n"
        
        print(f"✅ SSE stream completed for job {job_id} ({event_count} events sent)\n")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/api/job/{job_id}")
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get job status (for polling instead of SSE)

    Returns current status and result if complete
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobStatusResponse(
        job_id=job_id,
        status=job['status'],
        result=job.get('result'),
        error=job.get('error')
    )


async def run_recommendation_job(
    job_id: str,
    city: str,
    concept: str,
    limit: int,
    include_crime: bool
):
    """
    Background task: Run full recommendation pipeline with stage updates

    Stages:
    1. GEO - Identify top areas
    2. DEMO - Score demographics
    3. COMP - Count competitors
    4. TRANSIT - Calculate transit access
    5. TRAFFIC - Get traffic counts
    6. RENTS - Lookup rent bands
    7. REVENUE - Predict revenue
    """
    print(f"\n{'='*60}")
    print(f"🚀 BACKGROUND TASK STARTED")
    print(f"   Job ID: {job_id}")
    print(f"   City: {city}, Concept: {concept}, Limit: {limit}")
    print(f"{'='*60}\n")
    
    try:
        logger.info(f"Starting recommendation job {job_id} for {concept} in {city}")
        print(f"📊 Logger message sent")

        # Update job status to RUNNING
        job = job_manager.get_job(job_id)
        if job:
            job['status'] = 'running'
            logger.info(f"Job {job_id} status set to RUNNING")

        # Emit initial stage
        await job_manager.emit_stage_update(
            job_id=job_id,
            stage="GEO",
            status=StageStatus.RUNNING,
            ms=0
        )

        # Generate candidates (this handles all stages internally)
        start_time = asyncio.get_event_loop().time()

        candidates = await address_generator.generate_candidates(
            city=city,
            concept=concept,
            limit=limit,
            include_crime=include_crime
        )

        total_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

        # Emit completion for all stages (simplified for MVP)
        # In production, address_generator would emit these during processing
        await job_manager.emit_stage_update(
            job_id=job_id,
            stage="GEO",
            status=StageStatus.DONE,
            metrics={"areas_identified": 8},
            ms=total_ms // 7
        )

        await job_manager.emit_stage_update(
            job_id=job_id,
            stage="DEMO",
            status=StageStatus.DONE,
            metrics={"areas_scored": len(candidates)},
            ms=total_ms // 7
        )

        await job_manager.emit_stage_update(
            job_id=job_id,
            stage="COMP",
            status=StageStatus.DONE,
            metrics={"competitors_counted": len(candidates)},
            ms=total_ms // 7,
            cached=False
        )

        await job_manager.emit_stage_update(
            job_id=job_id,
            stage="TRANSIT",
            status=StageStatus.DONE,
            metrics={"transit_scored": len(candidates)},
            ms=total_ms // 7
        )

        await job_manager.emit_stage_update(
            job_id=job_id,
            stage="TRAFFIC",
            status=StageStatus.DONE,
            metrics={"traffic_points": 0},  # Not implemented yet
            ms=total_ms // 7
        )

        await job_manager.emit_stage_update(
            job_id=job_id,
            stage="RENTS",
            status=StageStatus.DONE,
            metrics={"rent_bands": 0},  # Not implemented yet
            ms=total_ms // 7
        )

        await job_manager.emit_stage_update(
            job_id=job_id,
            stage="REVENUE",
            status=StageStatus.DONE,
            metrics={"predictions": len(candidates)},
            ms=total_ms // 7
        )

        # Build response
        recommended_addresses = [
            RecommendedAddress(
                rank=candidate['rank'],
                address=candidate['address'],
                lat=candidate['lat'],
                lng=candidate['lng'],
                score=candidate['score'],
                revenue_min_eur=candidate['revenue_min_eur'],
                revenue_max_eur=candidate['revenue_max_eur'],
                confidence=candidate['confidence'],
                coverage=candidate['coverage'],
                why=candidate['why'],
                decision=candidate['decision'],
                decision_reasoning=candidate.get('decision_reasoning'),
                provenance=candidate.get('provenance'),
                area_id=candidate.get('area_id'),
                nearby_property_search_url=f"https://toimitilat.fi/haku?lat={candidate['lat']}&lon={candidate['lng']}&radius=500",
                metrics=candidate.get('metrics')
            )
            for candidate in candidates
        ]

        # Build weights info
        weights_info = WeightsInfo(
            weights_version="v1.0",
            weights={
                "population": 0.28,
                "income_fit": 0.22,
                "transit_access": 0.20,
                "competition_inverse": 0.15,
                "traffic_access": 0.10,
                "crime_penalty_cap": 0.05 if include_crime else 0.0
            },
            sources=[
                {"name": "Statistics Finland Population Grid", "refreshed_at": datetime.utcnow().isoformat()},
                {"name": "PAAVO Postal Demographics", "refreshed_at": datetime.utcnow().isoformat()},
                {"name": "OpenStreetMap Overpass", "refreshed_at": datetime.utcnow().isoformat()},
                {"name": "Digitransit Finland", "refreshed_at": datetime.utcnow().isoformat()}
            ]
        )

        result = RecommendResponse(
            job_id=job_id,
            city=city,
            concept=concept,
            top=recommended_addresses,
            method=weights_info,
            degraded=[]  # No degradation for MVP
        )

        # Complete job
        await job_manager.complete_job(
            job_id=job_id,
            result=result.dict()
        )

        logger.info(f"Job {job_id} completed with {len(candidates)} addresses in {total_ms}ms")

    except Exception as e:
        import traceback
        error_msg = f"Job {job_id} failed: {e}"
        error_trace = traceback.format_exc()
        
        print(f"\n{'='*60}")
        print(f"❌ BACKGROUND TASK FAILED")
        print(f"   Job ID: {job_id}")
        print(f"   Error: {error_msg}")
        print(f"   Traceback:")
        print(error_trace)
        print(f"{'='*60}\n")
        
        logger.error(error_msg, exc_info=True)
        await job_manager.fail_job(job_id, str(e))


@router.post("/api/pursue")
async def pursue_address(request: PursueRequest) -> PursueResponse:
    """
    Generate broker outreach email for a specific address

    Returns mailto: link and Gmail URL with pre-filled email template
    """
    from urllib.parse import quote

    # Generate email subject
    subject = f"Seeking {request.concept} space near {request.address}"

    # Generate email body
    body_lines = [
        "Hello,",
        "",
        f"I'm exploring potential locations for a {request.concept} concept and came across this area through market analysis.",
        "",
        f"Target Address: {request.address}",
        f"Location: {request.lat:.5f}, {request.lng:.5f}",
        "",
        "Our analysis shows this location has strong fundamentals:",
    ]

    # Add "why" bullets
    for reason in request.why:
        body_lines.append(f"• {reason}")

    body_lines.extend([
        "",
        f"Market Score: {request.score:.1f}/100",
        f"Projected Revenue: €{request.revenue_min_eur:,} - €{request.revenue_max_eur:,}/month",
        "",
        "I'm interested in learning about:",
        "• Available commercial properties within 200m of this location",
        "• Current asking rents and lease terms",
        "• Any upcoming vacancies or off-market opportunities",
        "",
        "Would you be available for a brief call this week to discuss options in this area?",
        "",
        "Best regards"
    ])

    body = "\n".join(body_lines)

    # URL-encode for mailto and Gmail
    subject_encoded = quote(subject)
    body_encoded = quote(body)

    # mailto: link (opens default email client)
    mailto_link = f"mailto:?subject={subject_encoded}&body={body_encoded}"

    # Gmail URL (opens Gmail in browser with pre-filled draft)
    gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&su={subject_encoded}&body={body_encoded}"

    logger.info(f"Generated pursue email for {request.address}")

    return PursueResponse(
        mailto_link=mailto_link,
        gmail_url=gmail_url,
        subject=subject,
        body=body
    )
