<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('system_logs', function (Blueprint $table) {
            $table->id();
            $table->string('type', 20)->default('audit'); // audit, security, system
            $table->foreignId('user_id')->nullable()->constrained()->nullOnDelete();
            $table->nullableMorphs('auditable'); 
            $table->text('description')->nullable(); 
            $table->json('old_values')->nullable();
            $table->json('new_values')->nullable();
            $table->ipAddress('ip')->nullable(); 
            $table->text('user_agent')->nullable();
            $table->string('event'); // 'created', 'updated', 'deleted'
            $table->string('url')->nullable();    // e.g., /api/v1/users/42
            $table->string('method', 10)->nullable(); // e.g., POST, PUT, DELETE
            $table->timestamps();

            $table->index('event');
            $table->index('created_at');
            $table->index('user_id');
            $table->index('type');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('system_logs');
    }
};
