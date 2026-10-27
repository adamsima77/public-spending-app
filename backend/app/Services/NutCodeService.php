<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\NutCode;
use Illuminate\Pagination\LengthAwarePaginator;

class NutCodeService
{
    public function getNutCodes(): LengthAwarePaginator
    {
        return NutCode::paginate(15);
    }

    public function createNutCode(array $validateEntryData): void
    {
        NutCode::create([
            'code' => $validateEntryData['code'],
            'name_sk', $validateEntryData['name_sk'],
            'level' => $validateEntryData['level'],
            'parent_code' => $validateEntryData['parent_code'],
        ]);
    }

    public function updateNutCode(NutCode $nutCode, array $validateEntry): void
    {
        $nutCode->update([
            'code' => $validateEntryData['code'],
            'name_sk', $validateEntryData['name_sk'],
            'level' => $validateEntryData['level'],
            'parent_code' => $validateEntryData['parent_code'],
        ]);
    }

    public function deleteNutCode(NutCode $nutCode): void
    {
        $nutCode->delete();
    }
}
