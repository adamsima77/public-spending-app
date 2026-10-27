<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Http\Resources\DownloadedFileResource;
use App\Models\DownloadedFile;
use App\Services\DownloadedFileService;

class DownloadedFileController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(DownloadedFileService $downloadedFileService)
    {
        $this->authorize('viewAny', DownloadedFile::class);
        $files = $downloadedFileService->getAllDownloadedFiles();

        return DownloadedFileResource::collection($files);
    }

    /**
     * Display the specified resource.
     */
    public function show(DownloadedFile $downloadedFile)
    {
        $this->authorize('view', $downloadedFile);

        return new DownloadedFileResource($downloadedFile);
    }
}
