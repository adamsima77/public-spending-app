<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Requests\DownloadedFileIndexRequest;
use App\Http\Resources\DownloadedFileResource;
use App\Models\DownloadedFile;
use App\Services\DownloadedFileService;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

class DownloadedFileController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(
        DownloadedFileIndexRequest $request,
        DownloadedFileService $downloadedFileService,
    ): AnonymousResourceCollection {
        $this->authorize('viewAny', DownloadedFile::class);
        $files = $downloadedFileService->getAllDownloadedFiles($request->validated());

        return DownloadedFileResource::collection($files);
    }

    /**
     * Display the specified resource.
     */
    public function show(DownloadedFile $downloadedFile): DownloadedFileResource
    {
        $this->authorize('view', $downloadedFile);
        $downloadedFile->load(['status', 'logs']);

        return new DownloadedFileResource($downloadedFile);
    }
}
