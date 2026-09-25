<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\SystemLog; 
use App\Service\SystemLogService;
use App\Http\Resource\SystemLogResource;

class SystemLogController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(SystemLogService $systemLogService)
    {
        $logs = $systemLogService->getAllLogs();
        return SystemLogResource::collection($logs);
    }

    /**
     * Display the specified resource.
     */
    public function show(SystemLog $systemLog)
    {
        return new SystemLogResource($systemLog);
    }

}
