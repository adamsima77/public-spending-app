<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Organization;
use Illuminate\Pagination\LengthAwarePaginator;

class OrganizationService
{
    /** @return LengthAwarePaginator<int, Organization> */
    public function getAllOrganizations(): LengthAwarePaginator
    {
        return Organization::paginate(15);
    }
}
