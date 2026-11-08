<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Resources\CodelistResource;
use App\Services\CodelistService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class FilterController extends Controller
{
    public function applicabilities(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->applicabilities(),
        );
    }

    public function awardCriterionTypes(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->awardCriterionTypes(),
        );
    }

    public function awardOutcomes(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->awardOutcomes(),
        );
    }

    public function companySizes(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->companySizes(),
        );
    }

    public function contractNatures(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->contractNatures(),
        );
    }

    public function durationUnits(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->durationUnits(),
        );
    }

    public function formTypes(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->formTypes(),
        );
    }

    public function legalBases(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->legalBases(),
        );
    }

    public function nonAwardReasons(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->nonAwardReasons(),
        );
    }

    public function noticeTypes(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->noticeTypes(),
        );
    }

    public function permissions(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->permissions(),
        );
    }

    public function procedureTypes(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->procedureTypes(),
        );
    }

    public function reservedProcurement(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->reservedProcurement(),
        );
    }

    public function submissionTypes(
        CodelistService $codelistService,
    ): AnonymousResourceCollection {
        return CodelistResource::collection(
            $codelistService->submissionTypes(),
        );
    }
}
