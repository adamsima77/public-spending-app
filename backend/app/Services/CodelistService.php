<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\ClApplicability;
use App\Models\ClAwardCriterionType;
use App\Models\ClAwardOutcome;
use App\Models\ClCompanySize;
use App\Models\ClContractNature;
use App\Models\ClDurationUnit;
use App\Models\ClFormType;
use App\Models\ClLegalBasis;
use App\Models\ClNonAwardReason;
use App\Models\ClNoticeType;
use App\Models\ClPermission;
use App\Models\ClProcedureType;
use App\Models\ClReservedProcurement;
use App\Models\ClSubmissionType;
use Illuminate\Database\Eloquent\Collection;

class CodelistService
{
    /** @return Collection<int, ClApplicability> */
    public function applicabilities(): Collection
    {
        return ClApplicability::all();
    }

    /** @return Collection<int, ClAwardCriterionType> */
    public function awardCriterionTypes(): Collection
    {
        return ClAwardCriterionType::all();
    }

    /** @return Collection<int, ClAwardOutcome> */
    public function awardOutcomes(): Collection
    {
        return ClAwardOutcome::all();
    }

    /** @return Collection<int, ClCompanySize> */
    public function companySizes(): Collection
    {
        return ClCompanySize::all();
    }

    /** @return Collection<int, ClContractNature> */
    public function contractNatures(): Collection
    {
        return ClContractNature::all();
    }

    /** @return Collection<int, ClDurationUnit> */
    public function durationUnits(): Collection
    {
        return ClDurationUnit::all();
    }

    /** @return Collection<int, ClFormType> */
    public function formTypes(): Collection
    {
        return ClFormType::all();
    }

    /** @return Collection<int, ClLegalBasis> */
    public function legalBases(): Collection
    {
        return ClLegalBasis::all();
    }

    /** @return Collection<int, ClNonAwardReason> */
    public function nonAwardReasons(): Collection
    {
        return ClNonAwardReason::all();
    }

    /** @return Collection<int, ClNoticeType> */
    public function noticeTypes(): Collection
    {
        return ClNoticeType::all();
    }

    /** @return Collection<int, ClPermission> */
    public function permissions(): Collection
    {
        return ClPermission::all();
    }

    /** @return Collection<int, ClProcedureType> */
    public function procedureTypes(): Collection
    {
        return ClProcedureType::all();
    }

    /** @return Collection<int, ClReservedProcurement> */
    public function reservedProcurement(): Collection
    {
        return ClReservedProcurement::all();
    }

    /** @return Collection<int, ClSubmissionType> */
    public function submissionTypes(): Collection
    {
        return ClSubmissionType::all();
    }
}
