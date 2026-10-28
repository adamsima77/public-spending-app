<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Resources\OrganizationResource;
use App\Models\Organization;
use App\Services\OrganizationService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class OrganizationController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(OrganizationService $organizationService): AnonymousResourceCollection
    {
        $organizations = $organizationService->getAllOrganizations();

        return OrganizationResource::collection($organizations);
    }

    /**
     * Display the specified resource.
     */
    public function show(Organization $organization): OrganizationResource
    {
        return new OrganizationResource($organization);
    }
}
