'use client'
import { useContext, useEffect, useState } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import { useRouter, usePathname } from "next/navigation";
import HeaderComponent from "@/app/components/HeaderComponent";
import LoadingComponent from "@/app/components/LoadingComponent";
import EventNavBarComponent from "@/app/components/EventNavBarComponent";
import validatePath from "@/app/utils/validadePath";
import getBasePath from "@/app/utils/getBasePath";
import SubmitFileComponent from "@/app/components/eventComponentes/SubmitFileComponent";
import AddPlayerComponent from "@/app/components/eventComponentes/AddPlayerComponent";
import AddStaffComponent from "@/app/components/eventComponentes/AddStaffComponent";
import AddManager from "@/app/components/eventComponentes/AddManager";
import CreateSumula from "@/app/components/eventComponentes/CreateSumula";
import PublishResults from "@/app/components/eventComponentes/PublishResults";
import DeleteSumula from "@/app/components/eventComponentes/DeleteSumula";
import Manage from "@/app/components/eventComponentes/Manage";

export default function Admin() {
  const { user, loading } = useContext(UserContext);
  const [canSee, setCanSee] = useState<boolean>(false);
  const router = useRouter();
  const params = usePathname().split("/");
  const currentId = parseInt(params[1]);
  const currentPath = params[2];
  const [userType, setUserType] = useState<UserType>('common');
  type UserType = 'player' | 'staff' | 'manager' | 'admin' | 'common';

  useEffect(() => {
    if (!user.access && !loading) {
      router.push("/");
    } else if (user.all_events) {
      const current = user.all_events.find(elem => elem.event?.id === currentId);
      if (current && current.role) {
        const isValidPath = validatePath(current.role, currentPath);
        if (isValidPath) {
          setUserType(current.role as UserType);
          setCanSee(true);
        } else {
          router.push(`/${currentId}/${getBasePath(current.role)}`);
        }
      } else {
        router.push("/contests");
      }
    }
  }, [user]);

  if (!canSee || loading) {
    return <LoadingComponent />;
  }

  return (
    <>
      <HeaderComponent />
      <div className="py-32">
        <SubmitFileComponent isManager={userType === 'manager'}/>
        <CreateSumula isImortal={false} buttonName="Súmula classificatória" />
        <CreateSumula isImortal={true} buttonName="Súmula imortais" />
        <AddPlayerComponent />
        {userType === 'admin' && (
          <>
            <AddStaffComponent />
            <AddManager />
            <PublishResults />
          </>
        )}
        <DeleteSumula />
        <Manage isAdmin={userType === 'admin'}/>
      </div>
      <EventNavBarComponent userType={userType} />
    </>
  );
}