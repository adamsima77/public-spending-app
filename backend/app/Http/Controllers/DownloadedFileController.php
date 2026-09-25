<?php

namespace App\Http\Controllers;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use App\Services\DownloadedFileService;
use App\Models\DownloadedFile;
use App\Http\Resources\DownloadedFileResource;

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
