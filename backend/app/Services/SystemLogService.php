<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\SystemLog;
use Illuminate\Pagination\LengthAwarePaginator;

class SystemLogService
{
    /** @return LengthAwarePaginator<int, SystemLog> */
    public function getAllLogs(): LengthAwarePaginator
    {
        return SystemLog::paginate(15);
    }
}
