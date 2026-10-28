<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Resources\NoticeLotResource;
use App\Models\NoticeLot;
use App\Services\NoticeLotService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class NoticeLotController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(NoticeLotService $noticeLotService): AnonymousResourceCollection
    {
        $lots = $noticeLotService->getLots();

        return NoticeLotResource::collection($lots);
    }

    /**
     * Display the specified resource.
     */
    public function show(NoticeLot $noticeLot): NoticeLotResource
    {
        return new NoticeLotResource($noticeLot);
    }
}
