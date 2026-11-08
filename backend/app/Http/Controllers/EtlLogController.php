<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\EtlLogIndexRequest;
use App\Http\Resources\EtlLogResource;
use App\Models\EtlLog;
use App\Services\EtlLogService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class EtlLogController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(EtlLogIndexRequest $request, EtlLogService $etlLogService): AnonymousResourceCollection
    {
        $this->authorize('viewAny', EtlLog::class);
        $logs = $etlLogService->getAllLogs($request->validated());

        return EtlLogResource::collection($logs);
    }

    /**
     * Display the specified resource.
     */
    public function show(EtlLog $etlLog): EtlLogResource
    {
        $this->authorize('view', $etlLog);
        $etlLog->load(['file.status']);

        return new EtlLogResource($etlLog);
    }
}
