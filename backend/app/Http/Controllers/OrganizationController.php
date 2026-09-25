<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Http\Resources\OrganizationResource;
use App\Services\OrganizationService; 
use App\Models\Organization;

class OrganizationController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(OrganizationService $organizationService)
    {
        $organizations = $organizationService->getAllOrganizations();
        return OrganizationResource::collection($organizations);
    }


    /**
     * Display the specified resource.
     */
    public function show(Organization $organization)
    {
        return new OrganizationResource($organization);
    }
}
