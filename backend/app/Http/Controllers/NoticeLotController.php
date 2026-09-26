<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\Response;
use App\Http\Resources\NoticeLotResource;
use App\Models\NoticeLot;
use App\Services\NoticeLotService;

class NoticeLotController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(NoticeLotService $noticeLotService)
    {
        $lots = $noticeLotService->getLots();
        return NoticeLotResource::collection($lots);
    }

    /**
     * Display the specified resource.
     */
    public function show(NoticeLot $noticeLot)
    {
        return new NoticeLotResource($noticeLot);
    }
}
