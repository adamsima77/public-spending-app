<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\CpvCodeIndexRequest;
use App\Http\Resources\CpvCodeResource;
use App\Models\CpvCode;
use App\Services\CpvCodeService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class CpvCodeController extends Controller
{
    public function index(
        CpvCodeIndexRequest $request,
        CpvCodeService $cpvCodeService,
    ): AnonymousResourceCollection {
        return CpvCodeResource::collection($cpvCodeService->getAllCpvCodes($request->validated()));
    }

    public function show(CpvCode $cpvCode): CpvCodeResource
    {
        return new CpvCodeResource($cpvCode);
    }
}
