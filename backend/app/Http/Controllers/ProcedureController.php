<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\ProcedureService;
use App\Http\Resources\ProcedureResource;
use App\Models\Procedure;

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
