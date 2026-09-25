<?php

namespace App\Services;
use App\Models\Procedure;
use Illuminate\Pagination\LengthAwarePaginator;

class ProcedureService {

    public function getAllProcedures(): LengthAwarePaginator
    {
        return Procedure::paginate(15);
    }
}