<?php

namespace App\Http\Controllers;

use App\Http\Resources\SystemLogResource;
use App\Services\SystemLogService;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use App\Models\SystemLog;

class SystemLogController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(SystemLogService $systemLogService)
    {
        $this->authorize('viewAny', SystemLog::class);
        $logs = $systemLogService->getAllLogs();
        return SystemLogResource::collection($logs);
    }

    /**
     * Display the specified resource.
     */
    public function show(SystemLog $systemLog)
    {
        $this->authorize('view', $systemLog);
        return new SystemLogResource($systemLog);
    }

}
