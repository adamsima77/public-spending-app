<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\NoticeIndexRequest;
use App\Http\Resources\NoticeResource;
use App\Models\Notice;
use App\Services\NoticeService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class NoticeController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(NoticeIndexRequest $request, NoticeService $noticeService): AnonymousResourceCollection
    {
        $notices = $noticeService->getNotices($request->validated());

        return NoticeResource::collection($notices);
    }

    /**
     * Display the specified resource.
     */
    public function show(Notice $notice): NoticeResource
    {
        $notice->load([
            'procedure.buyer.nutCode',
            'procedure.buyer.companySize',
            'procedure.cpvCode',
            'procedure.nutCode',
            'procedure.procedureType',
            'procedure.contractNature',
            'formType',
            'noticeType',
            'legalBasis',
            'lotResults.lot',
            'lotResults.awardOutcome',
            'lotResults.nonAwardReason',
            'lotResults.submissionStats',
            'lotTenders.lot',
            'lotTenders.organizations',
            'lotTenders.subcontractingApplicability',
            'lotTenders.settledContracts',
            'settledContracts.tenders.organizations',
        ]);

        return new NoticeResource($notice);
    }
}
