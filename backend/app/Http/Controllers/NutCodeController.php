<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Resources\NutCodeResource;
use App\Models\NutCode;
use App\Services\NutCodeService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class NutCodeController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(NutCodeService $nutCodeService): AnonymousResourceCollection
    {
        $nutCodes = $nutCodeService->getNutCodes();

        return NutCodeResource::collection($nutCodes);
    }

    /**
     * Display the specified resource.
     */
    public function show(NutCode $nutCode): NutCodeResource
    {
        return new NutCodeResource($nutCode);
    }
}
