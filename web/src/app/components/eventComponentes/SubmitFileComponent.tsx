import React, { useContext, useState } from "react";
import { UserContext } from "../../contexts/UserContext";
import { usePathname } from "next/navigation";
import request from "@/app/utils/request";
import toast from "react-hot-toast";
import { formDataSettings } from "@/app/utils/formDataSettings";
import { isAxiosError } from "axios";
import AddPlayerComponent from "./AddPlayerComponent";

interface SubmitFileComponentProps {
    isManager: boolean;
}

export default function SubmitFileComponent(props: SubmitFileComponentProps) {
    const [playerFile, setPlayerFile] = useState<File | null>(null);
    const [staffFile, setStaffFile] = useState<File | null>(null);
    const currentId = usePathname().split("/")[1];
    const { user } = useContext(UserContext);

    const handlePlayerFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setPlayerFile(event.target.files[0]);
        }
    }
    const handleStaffFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setStaffFile(event.target.files[0]);
        }
    }

    const handlePlayerSubmit = async () => {
        if (playerFile) {
            const formData = new FormData();
            formData.append("file", playerFile);
            try {
                const response = await request.post(`/api/upload-player/?event_id=${currentId}`, formData, formDataSettings(user.access));
                if (response.status === 201) {
                    if (typeof response.data === 'object' && response.data !== null && 'message' in response.data && 'errors' in response.data) {
                        toast.success(response.data.message, { duration: 6000 });
                        toast(response.data.errors, { duration: 6000, icon: '⚠️' });
                    } else {
                        toast.success(response.data);
                    }
                }
            } catch (error: unknown) {
                if (isAxiosError(error)) {
                    const { data } = error.response || {};
                    const errorMessage = data.errors || "Erro desconhecido.";
                    toast.error(errorMessage);
                }
                console.log(error);
            }
        } else {
            toast.error("Selecione um arquivo para enviar!");
        }
    }

    const handleStaffSubmit = async () => {
        if (staffFile) {
            const formData = new FormData();
            formData.append("file", staffFile);
            try {
                const response = await request.post(`/api/upload-staff/?event_id=${currentId}`, formData, formDataSettings(user.access));
                if (response.status === 201) {
                    toast.success(response.data);
                }
            } catch (error: unknown) {
                if (isAxiosError(error)) {
                    const { data } = error.response || {};
                    const errorMessage = data.errors || "Erro desconhecido.";
                    toast.error(errorMessage);
                }
                console.log(error);
            }
        } else {
            toast.error("Selecione um arquivo para enviar!");
        }
    }
    return (
        <div className="grid justify-center items-center gap-5">
            <div className="grid gap-4 bg-neutral-100 rounded-2xl py-6 shadow-sm md:px-4 ">
                <p className="font-semibold text-primary pl-4">ADICIONAR JOGADORES</p>
                <input className="pl-4" type="file" onChange={handlePlayerFileChange} />
                <button className="bg-primary font-medium text-white rounded-md mx-4 p-2" onClick={handlePlayerSubmit}>Enviar</button>
            </div>
            {!props.isManager && <div className="grid gap-4 bg-neutral-100 rounded-2xl py-6 shadow-sm">
                <p className="font-semibold text-primary pl-4">ADICIONAR STAFF</p>
                <input className="pl-4" type="file" onChange={handleStaffFileChange} />
                <button className="bg-primary font-medium text-white rounded-md mx-4 py-2" onClick={handleStaffSubmit}>Enviar</button>
            </div>}
        </div>
    );
}
