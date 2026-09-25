<?php

namespace App\Services;
use App\Models\EtlLog;
use Illuminate\Pagination\LengthAwarePaginator;

class EtlLogService {

    public function getAllLogs(): LengthAwarePaginator
    {
        return EtlLog::paginate(15);
    } 
}