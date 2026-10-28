<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\EtlLog;
use Illuminate\Pagination\LengthAwarePaginator;

class EtlLogService
{
    /** @return LengthAwarePaginator<int, EtlLog> */
    public function getAllLogs(): LengthAwarePaginator
    {
        return EtlLog::paginate(15);
    }
}
