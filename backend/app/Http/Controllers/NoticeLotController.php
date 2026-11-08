<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\NoticeLotIndexRequest;
use App\Http\Resources\NoticeLotResource;
use App\Models\NoticeLot;
use App\Services\NoticeLotService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class NoticeLotController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(NoticeLotIndexRequest $request, NoticeLotService $noticeLotService): AnonymousResourceCollection
    {
        $lots = $noticeLotService->getLots($request->validated());

        return NoticeLotResource::collection($lots);
    }

    /**
     * Display the specified resource.
     */
    public function show(NoticeLot $noticeLot): NoticeLotResource
    {
        $noticeLot->load([
            'procedure.buyer.nutCode',
            'procedure.buyer.companySize',
            'procedure.cpvCode',
            'procedure.nutCode',
            'procedure.procedureType',
            'procedure.contractNature',
            'cpvCode',
            'nutCode',
            'durationUnit',
            'awardCriterionType',
            'reservedExecutionType',
            'reservedParticipationType',
            'einvoicingPermission',
            'variantsApplicability',
            'suppliers.nutCode',
            'suppliers.companySize',
            'lotResults.awardOutcome',
            'lotResults.nonAwardReason',
            'lotResults.submissionStats',
            'tenders.organizations.nutCode',
            'tenders.organizations.companySize',
            'tenders.subcontractingApplicability',
            'tenders.settledContracts',
        ]);

        return new NoticeLotResource($noticeLot);
    }
}
