<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Resources\EtlLogResource;
use App\Models\EtlLog;
use App\Services\EtlLogService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class EtlLogController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(EtlLogService $etlLogService): AnonymousResourceCollection
    {
        $this->authorize('viewAny', EtlLog::class);
        $logs = $etlLogService->getAllLogs();

        return EtlLogResource::collection($logs);
    }

    /**
     * Display the specified resource.
     */
    public function show(EtlLog $etlLog): EtlLogResource
    {
        $this->authorize('view', $etlLog);

        return new EtlLogResource($etlLog);
    }
}
