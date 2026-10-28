<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\NutCode;
use Illuminate\Pagination\LengthAwarePaginator;

class NutCodeService
{
    /** @return LengthAwarePaginator<int, NutCode> */
    public function getNutCodes(): LengthAwarePaginator
    {
        return NutCode::paginate(15);
    }

    /** @param array<string, mixed> $validatedData */
    public function createNutCode(array $validatedData): void
    {
        NutCode::create($validatedData);
    }

    /** @param array<string, mixed> $validatedData */
    public function updateNutCode(NutCode $nutCode, array $validatedData): void
    {
        $nutCode->update($validatedData);
    }

    public function deleteNutCode(NutCode $nutCode): void
    {
        $nutCode->delete();
    }
}
