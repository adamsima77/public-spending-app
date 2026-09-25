<?php

namespace App\Services;
use Illuminate\Pagination\LengthAwarePaginator;
use App\Models\Organization;

class OrganizationService {

    public function getAllOrganizations(): LengthAwarePaginator
    {
        return Organization::paginate(15);
    }
}