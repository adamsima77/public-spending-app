<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Procedure;
use Illuminate\Pagination\LengthAwarePaginator;

class ProcedureService
{
    /** @return LengthAwarePaginator<int, Procedure> */
    public function getAllProcedures(): LengthAwarePaginator
    {
        return Procedure::paginate(15);
    }
}
