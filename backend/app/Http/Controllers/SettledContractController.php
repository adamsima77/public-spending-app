<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\SettledContractIndexFormRequest;
use App\Http\Requests\SettledContractKpi;
use App\Http\Resources\SettledContractKpiResource;
use App\Http\Resources\SettledContractResource;
use App\Models\SettledContract;
use App\Services\SettledContractService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class SettledContractController extends Controller
{
    public function __construct(private readonly SettledContractService $service) {}

    public function index(SettledContractIndexFormRequest $request): AnonymousResourceCollection
    {
        return SettledContractResource::collection(
            $this->service->getSettledContracts($request->validated()),
        );
    }

    public function show(SettledContract $settledContract): SettledContractResource
    {
        return new SettledContractResource(
            $this->service->getSettledContract($settledContract),
        );
    }

    public function kpis(SettledContractKpi $request): SettledContractKpiResource
    {
        return new SettledContractKpiResource(
            $this->service->getKpis($request->validated()),
        );
    }
}
