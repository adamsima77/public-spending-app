<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\Response;
use App\Services\EtlLogService;
use App\Models\EtlLog;
use App\Http\Resources\EtlLogResource;

class EtlLogController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(EtlLogService $etlLogService)
    {
        $this->authorize('viewAny', EtlLog::class);
        $logs = $etlLogService->getAllLogs();
        return EtlLogResource::collection($logs);
    }


    /**
     * Display the specified resource.
     */
    public function show(EtlLog $etlLog)
    {
        $this->authorize('view', $etlLog);
        return new EtlLogResource($etlLog);
    }
}
