<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Resources\ProcedureResource;
use App\Models\Procedure;
use App\Services\ProcedureService;

class ProcedureController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(ProcedureService $procedureService)
    {
        $procedures = $procedureService->getAllProcedures();

        return ProcedureResource::collection($procedures);
    }

    /**
     * Display the specified resource.
     */
    public function show(Procedure $procedure)
    {
        return new ProcedureResource($procedure);
    }
}
