<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\Response;
use App\Http\Resources\NutCodeResource;
use App\Models\NutCode;
use App\Services\NutCodeService;
use App\Http\Requests\StoreNutCodeRequest;
use App\Http\Requests\UpdateNutCodeRequest;

class NutCodeController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(NutCodeService $nutCodeService)
    {
        $nutCodes = $nutCodeService->getNutCodes();
        return NutCodeResource::collection($nutCodes);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(StoreNutCodeRequest $request, NutCodeService $nutCodeService)
    {
        $this->authorize('create', NutCode::class);
        $validatedData = $request->validated();

        $nutCodeService->createNutCode($validatedData);
        return response()->json(null, Response::HTTP_CREATED);
    }

    /**
     * Display the specified resource.
     */
    public function show(NutCode $nutCode)
    {
        return new NutCodeResource($nutCode);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateNutCodeRequest $request, NutCode $nutCode, NutCodeService $nutCodeService)
    {
        $this->authorize('update', $nutCode);
        $validateEntry = $request->validated();
        $nutCodeService->updateNutCode($nutCode, $validateEntry);
        return response()->json(['message' => 'Nut code bol upravený !'], Response::HTTP_OK);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(NutCode $nutCode, NutCodeService $nutCodeService)
    {
        $this->authorize('destroy', $nutCode);
        $nutCodeService->deleteNutCode($nutCode);
        return response()->json(['message' => 'Nut code bol úspešne vymazaný !'], Response::HTTP_OK);
    }
}
