<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('cl_reserved_procurement', function (Blueprint $table) {
            $table->string('code', 64)->primary();
            $table->string('label_sk', 255);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('cl_reserved_procurement');
    }
};