<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\SystemLogIndexRequest;
use App\Http\Resources\SystemLogResource;
use App\Models\SystemLog;
use App\Services\SystemLogService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class SystemLogController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(
        SystemLogIndexRequest $request,
        SystemLogService $systemLogService,
    ): AnonymousResourceCollection {
        $this->authorize('viewAny', SystemLog::class);
        $logs = $systemLogService->getAllLogs($request->validated());

        return SystemLogResource::collection($logs);
    }

    /**
     * Display the specified resource.
     */
    public function show(SystemLog $systemLog): SystemLogResource
    {
        $this->authorize('view', $systemLog);
        $systemLog->load(['user.role']);

        return new SystemLogResource($systemLog);
    }
}
