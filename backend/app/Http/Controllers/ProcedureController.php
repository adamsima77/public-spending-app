<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\ProcedureIndexRequest;
use App\Http\Resources\ProcedureResource;
use App\Models\Procedure;
use App\Services\ProcedureService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class ProcedureController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(
        ProcedureIndexRequest $request,
        ProcedureService $procedureService,
    ): AnonymousResourceCollection {
        $procedures = $procedureService->getAllProcedures($request->validated());

        return ProcedureResource::collection($procedures);
    }

    /**
     * Display the specified resource.
     */
    public function show(Procedure $procedure): ProcedureResource
    {
        $procedure->load([
            'buyer.nutCode',
            'buyer.companySize',
            'cpvCode',
            'nutCode',
            'procedureType',
            'contractNature',
            'notices.formType',
            'notices.noticeType',
            'noticeLots.cpvCode',
            'noticeLots.nutCode',
        ]);

        return new ProcedureResource($procedure);
    }
}
